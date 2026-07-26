
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import re

@dataclass
class Merchant:
    name:str
    category:str="Unknown"
    frequency:str="Unknown"
    country:str="Unknown"
    risk:str="Unknown"
    confidence_boost:int=0
    aliases:List[str]=field(default_factory=list)

class MerchantRegistry:
    def __init__(self,data_dir:Optional[str]=None):
        self.data_dir=Path(data_dir) if data_dir else Path(__file__).resolve().parent.parent/"data"
        self.merchants={}
        self.alias_map={}
        self.blacklist=set()
        self._load_whitelist()
        self._load_blacklist()
        self._load_database()

    @staticmethod
    def normalize(text:str)->str:
        text="" if text is None else str(text).upper()
        text=re.sub(r"\d{6,}"," ",text)
        text=re.sub(r"[*_/.,\-]"," ",text)
        text=re.sub(r"\s+"," ",text).strip()
        words=[w for w in text.split() if w not in {"LTD","LIMITED","INC","LLC","PTY","SERVICES","SERVICE"}]
        return " ".join(words)

    def _load_whitelist(self):
        f=self.data_dir/"subscription_whitelist.csv"
        if not f.exists(): return
        for _,r in pd.read_csv(f).fillna("").iterrows():
            m=Merchant(
                name=r["Merchant"],
                category=r.get("Category","Unknown"),
                frequency=r.get("Frequency","Unknown"),
                country=r.get("Country","Unknown"),
                risk=r.get("Risk","Unknown"),
                confidence_boost=int(r.get("ConfidenceBoost",0))
            )
            aliases=[a.strip() for a in str(r.get("Aliases","")).split(",") if a.strip()]
            m.aliases=aliases
            k=self.normalize(m.name)
            self.merchants[k]=m
            self.alias_map[k]=k
            for a in aliases:
                self.alias_map[self.normalize(a)]=k

    def _load_blacklist(self):
        f=self.data_dir/"subscription_blacklist.csv"
        if not f.exists(): return
        for _,r in pd.read_csv(f).iterrows():
            self.blacklist.add(self.normalize(r["Merchant"]))

    def _load_database(self):
        f=self.data_dir/"merchant_database.csv"
        if not f.exists(): return
        for _,r in pd.read_csv(f).fillna("").iterrows():
            k=self.normalize(r["Merchant"])
            if k in self.merchants: continue
            self.merchants[k]=Merchant(
                name=r["Merchant"],
                category=r.get("Category","Unknown"),
                frequency=r.get("Frequency","Unknown")
            )
            self.alias_map[k]=k

    def is_blacklisted(self,merchant:str)->bool:
        n=self.normalize(merchant)
        return any(b and b in n for b in self.blacklist)

    def find(self,merchant:str)->Merchant:
        n=self.normalize(merchant)
        if n in self.alias_map:
            return self.merchants[self.alias_map[n]]
        best=""
        for a,c in self.alias_map.items():
            if a in n and len(a)>len(best):
                best=a
        return self.merchants[self.alias_map[best]] if best else Merchant(name=merchant)

    def classify(self,merchant:str)->dict:
        if self.is_blacklisted(merchant):
            return {"merchant":merchant,"subscription":False,"confidence":0,"reason":"Merchant appears in blacklist."}
        m=self.find(merchant)
        conf=m.confidence_boost
        reasons=[]
        if conf:
            reasons.append("Known subscription merchant.")
        if m.frequency.lower()=="monthly":
            conf+=20
            reasons.append("Typical monthly billing.")
        conf=min(conf,100)
        return {
            "merchant":merchant,
            "canonical":m.name,
            "subscription":conf>=60,
            "confidence":conf,
            "category":m.category,
            "frequency":m.frequency,
            "country":m.country,
            "risk":m.risk,
            "reason":" ".join(reasons) if reasons else "Unknown merchant."
        }
