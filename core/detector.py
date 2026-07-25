
# detector.py
from __future__ import annotations
import pandas as pd
from core.classifier import SubscriptionClassifier, SubscriptionType
from core.constants import MIN_OCCURRENCES,SUBSCRIPTION_COLUMNS,VALID_TRANSACTION_STATUSES
from core.utils import average_interval,coefficient_of_variation,empty_dataframe

class SubscriptionDetector:
    def __init__(self):
        self.classifier=SubscriptionClassifier()
    def detect(self,df:pd.DataFrame,confidence_threshold:int=60)->pd.DataFrame:
        if df.empty:
            return empty_dataframe(SUBSCRIPTION_COLUMNS)
        data=df.copy()
        data["Status"]=data["Status"].astype(str).str.upper().str.strip()
        data=data[data["Status"].isin({s.upper() for s in VALID_TRANSACTION_STATUSES})]
        out=[]
        for acct,g in data.groupby("Account ID"):
            rows=[]
            for _,tx in g.iterrows():
                r=self.classifier.classify(tx["Transaction For"])
                if r.subscription_type==SubscriptionType.UNKNOWN: continue
                t=tx.copy()
                t["Merchant"]=r.merchant; t["Category"]=r.category; t["Frequency"]=r.frequency; t["ClassConfidence"]=r.confidence
                rows.append(t)
            if not rows: continue
            cdf=pd.DataFrame(rows)
            for merchant,mg in cdf.groupby("Merchant"):
                if len(mg)<MIN_OCCURRENCES: continue
                mg=mg.sort_values("Transaction Date")
                conf=min(int(mg["ClassConfidence"].mean()*0.7+max(0,30-coefficient_of_variation(list(mg["Amount"])))),100)
                if conf<confidence_threshold: continue
                last=mg.iloc[-1]
                out.append({"Account ID":acct,"Customer":last["Name"],"Merchant":merchant,"Category":last["Category"],"Frequency":last["Frequency"],"Occurrences":len(mg),"Average Amount":round(mg["Amount"].mean(),2),"Last Amount":last["Amount"],"First Charge":mg.iloc[0]["Transaction Date"],"Last Charge":last["Transaction Date"],"Average Interval":average_interval(list(mg["Transaction Date"])),"Confidence":conf})
        return empty_dataframe(SUBSCRIPTION_COLUMNS) if not out else pd.DataFrame(out).sort_values(["Confidence","Occurrences"],ascending=[False,False]).reset_index(drop=True)

def detect_subscriptions(df,confidence_threshold=60):
    return SubscriptionDetector().detect(df,confidence_threshold)

def subscription_summary(df):
    if df.empty: return {"subscriptions":0,"customers":0,"monthly_spend":0}
    return {"subscriptions":len(df),"customers":df["Account ID"].nunique(),"monthly_spend":round(df["Average Amount"].sum(),2)}
