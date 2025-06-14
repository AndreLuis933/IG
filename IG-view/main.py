import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from database import SUPABASE_CLIENT

supabase = SUPABASE_CLIENT
response = supabase.table("produtos").select("*").limit(10).execute()
print(response.data)
