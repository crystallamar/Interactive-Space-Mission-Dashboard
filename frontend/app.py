import datetime
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000"

# Search starts open for user ease
st.set_page_config(layout="wide", initial_sidebar_state="expanded") 

# Fetch dropdown options and price range from API on startup
@st.cache_data
def get_options():
    response = requests.get(f"{API_URL}/options")
    return response.json()

@st.cache_data
def get_price_range():
    response = requests.get(f"{API_URL}/price-range")
    return response.json()

options = get_options()
price_range_bounds = get_price_range()

min_price = price_range_bounds["min"]
max_price = price_range_bounds["max"]

st.sidebar.title("Search By:")
st.title('Space Missions Dashboard')

# Table
company = st.sidebar.selectbox("Company", ["All"] + options["companies"])
location = st.sidebar.selectbox("Location", ["All"] + options["locations"])
date_from = st.sidebar.text_input("Date From (YYYY-MM-DD)", placeholder="e.g. 1957-10-04")
date_to = st.sidebar.text_input("Date To (YYYY-MM-DD)", placeholder="e.g. 2020-12-31")
time_input = st.sidebar.text_input("Time (HH:MM:SS)", placeholder=datetime.datetime.now().strftime("%H:%M:%S"))
rocket = st.sidebar.selectbox("Rocket", ["All"] + options["rockets"])
mission = st.sidebar.selectbox("Mission", ["All"] + options["missions"])
rocket_status = st.sidebar.selectbox("Rocket Status", ["All"] + options["rocket_statuses"])
price_range = st.sidebar.slider("Price Range (in million USD)", min_value=min_price, max_value=max_price, value=(min_price, max_price))
mission_status = st.sidebar.selectbox("Mission Status", ["All"] + options["mission_statuses"])

# Search by on side bar and filter by search criteria
params = {}
if company != "All":
    params["company"] = company
if location != "All":
    params["location"] = location
if date_from and date_from.strip() != "":
    try:
        pd.Timestamp(date_from.strip())
        params["date_from"] = date_from.strip()
    except Exception:
        st.warning("Invalid date format for 'Date From'. Please use YYYY-MM-DD.")
        st.stop()
if date_to and date_to.strip() != "":
    try:
        pd.Timestamp(date_to.strip())
        params["date_to"] = date_to.strip()
    except Exception:
        st.warning("Invalid date format for 'Date To'. Please use YYYY-MM-DD.")
        st.stop()
if time_input and time_input.strip() != "":
    params["time"] = time_input.strip()
if rocket != "All":
    params["rocket"] = rocket
if mission != "All":
    params["mission"] = mission
if rocket_status != "All":
    params["rocket_status"] = rocket_status
if mission_status != "All":
    params["mission_status"] = mission_status
if price_range != (min_price, max_price):
    params["price_min"] = price_range[0]
    params["price_max"] = price_range[1]

# Fetch filtered missions from API
response = requests.get(f"{API_URL}/missions", params=params)
filtered_df = pd.DataFrame(response.json())

# Handle empty results
if filtered_df.empty:
    st.warning("No missions found for the selected filters.")
    st.stop()

filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])

# Show summary metrics
st.subheader("Mission Data")
total = len(filtered_df)
successful = len(filtered_df[filtered_df["MissionStatus"] == "Success"])
failed = len(filtered_df[filtered_df["MissionStatus"] == "Failure"])
partial = len(filtered_df[filtered_df["MissionStatus"] == "Partial Failure"])
success_rate = round(successful / total * 100, 2) if total > 0 else 0

col_s1, col_s2, col_s3, col_s4, col_s5, col_s6 = st.columns(6)
col_s1.metric("Total Missions", total)
col_s2.metric("Successful", successful)
col_s3.metric("Failed", failed)
col_s4.metric("Partial Failure", partial)
col_s5.metric("Prelaunch Failure", total - successful - failed - partial)
col_s6.metric("Success Rate", f"{success_rate}%")

# Charts at the top
col1, col2, col3 = st.columns(3)

# Count missions per decade
with col1:
    df_year = filtered_df.copy()
    df_year["Year"] = df_year["Date"].dt.year
    df_year["Decade"] = (df_year["Year"] // 10 * 10).astype(str) + "s"
    decade_counts = df_year.groupby("Decade").size()
    valid_decades = decade_counts[decade_counts > 0].index
    df_year = df_year[df_year["Decade"].isin(valid_decades)]
    if df_year.empty:
        st.info("No data available for this filter selection")
    else:
        decade_stats = df_year.groupby("Decade").apply(
            lambda x: round((x["MissionStatus"] == "Success").sum() / len(x) * 100, 2),
            include_groups=False
        ).reset_index(name="SuccessRate")
        fig1 = px.bar(decade_stats, x="Decade", y="SuccessRate",
                      title="Success Rate by Decade (%)",
                      labels={"SuccessRate": "Success Rate (%)"},
                      range_y=[0, 100])
        fig1.update_layout(
            margin=dict(t=60, b=40),
            yaxis=dict(tick0=0, dtick=10)
        )
        st.plotly_chart(fig1, use_container_width=True)

# Top 10 companies by mission count
with col2:
    if filtered_df.empty:
        st.info("No data available for this filter selection")
    else:
        top_companies = filtered_df["Company"].value_counts().head(10).reset_index()
        top_companies.columns = ["Company", "Count"]
        top_companies = top_companies.sort_values("Count", ascending=True)
        fig2 = px.bar(top_companies, x="Count", y="Company", orientation="h",
                      title="Top 10 Companies by Mission Count",
                      labels={"Count": "Missions"})
        fig2.update_layout(
            margin=dict(t=60, b=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

# Top 10 locations by mission count
with col3:
    if filtered_df.empty:
        st.info("No data available for this filter selection")
    else:
        top_locations = filtered_df["Location"].value_counts().head(10).reset_index()
        top_locations.columns = ["Location", "Count"]
        fig3 = px.pie(top_locations, names="Location", values="Count",
                      title="Most Popular Launch Locations (Top 10)")
        fig3.update_traces(
            textposition="inside",
            textinfo="percent",
            insidetextorientation="auto",
            showlegend=True,
            domain=dict(x=[0, 0.7])
        )
        fig3.update_layout(
            title_x=0,
            height=425,
            margin=dict(t=60, b=200, l=0, r=0),  
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.35,
                font=dict(size=8)
            )
        )
        st.plotly_chart(fig3, use_container_width=True)

# Show results
st.dataframe(filtered_df, height=500)



# Functions
# 1 Get Mission Count By Company
def getMissionCountByCompany(companyName: str) -> int:
    response = requests.get(f"{API_URL}/missions", params={"company": companyName})
    return len(response.json())

# 2 Get Success Rate by Company
def getSuccessRate(companyName: str) -> float:
    response = requests.get(f"{API_URL}/missions", params={"company": companyName})
    missions = response.json()
    if len(missions) == 0:
        return 0.0
    success_count = sum(1 for m in missions if m["MissionStatus"] == "Success")
    return round(success_count / len(missions) * 100, 2)

# 3 Get Missions By Date Range
def getMissionsByDateRange(startDate: str, endDate: str) -> list:
    try:
        response = requests.get(f"{API_URL}/missions", params={"date_from": startDate, "date_to": endDate})
        missions = response.json()
        return sorted([m["Mission"] for m in missions])
    except Exception:
        return []

# 4 Get Top Companies By Mission Count
def getTopCompaniesByMissionCount(n: int) -> list:
    if n <= 0:
        return []
    response = requests.get(f"{API_URL}/missions")
    missions = response.json()
    df_temp = pd.DataFrame(missions)
    top_companies = df_temp["Company"].value_counts().reset_index()
    top_companies.columns = ["Company", "MissionCount"]
    top_companies = top_companies.sort_values(by=["MissionCount", "Company"], ascending=[False, True])
    return [(row["Company"], int(row["MissionCount"])) for _, row in top_companies.head(n).iterrows()]

# 5 Get Mission Status Count
def getMissionStatusCount() -> dict:
    response = requests.get(f"{API_URL}/stats")
    stats = response.json()
    return {
        "Success": stats["successful"],
        "Failure": stats["failed"],
        "Partial Failure": stats["partial_failure"],
        "Prelaunch Failure": stats["prelaunch_failure"]
    }

# 6 Get Missions By Year
def getMissionsByYear(year: int) -> int:
    try:
        response = requests.get(f"{API_URL}/missions")
        missions = response.json()
        return sum(1 for m in missions if m["Date"] and m["Date"].startswith(str(year)))
    except Exception:
        return 0

# 7 Get Most Used Rocket
def getMostUsedRocket() -> str:
    response = requests.get(f"{API_URL}/missions")
    missions = response.json()
    df_temp = pd.DataFrame(missions)
    rockets = df_temp["Rocket"].value_counts()
    max_count = rockets.iloc[0]
    top_rockets = rockets[rockets == max_count].index.tolist()
    return sorted(top_rockets)[0] if top_rockets else "N/A"

# 8 Get Average Missions Per Year
def getAverageMissionsPerYear(startYear: int, endYear: int) -> float:
    response = requests.get(f"{API_URL}/missions", params={"date_from": f"{startYear}-01-01", "date_to": f"{endYear}-12-31"})
    missions = response.json()
    num_years = endYear - startYear + 1
    if num_years > 0:
        return round(len(missions) / num_years, 2)
    else:
        return 0.0