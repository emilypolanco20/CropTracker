import pandas as pd
import streamlit as st

# Load the crops data
@st.cache_data
def load_crops_data(file_path):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Strip extra spaces from column names
    return df

# Optimized Knapsack problem function to maximize profit
def knapsack(crops, season, current_day, money):
    # Determine the remaining days in the season based on the current day
    total_season_days = {"Spring": 28, "Summer": 28, "Fall": 28}
    days_left = total_season_days.get(season, 28) - current_day
    
    # Create a dp array where dp[i] represents the maximum profit with i money
    dp = [0] * (money + 1)
    crop_combinations = [[] for _ in range(money + 1)]
    
    # Iterate over each crop
    for _, crop in crops.iterrows():
        # Skip crops that cannot be grown in the remaining days
        if crop["Growth Time"] > days_left:
            continue
        
        # Max seeds you can afford with available money
        max_seeds = money // crop["Seed Cost"]
        
        # Calculate maximum seeds that can be planted in the available days
        max_seeds = min(max_seeds, days_left // crop["Growth Time"])
        
        if max_seeds == 0:
            continue  # Skip crops that cannot be planted

        total_profit = crop["Selling Price"] * max_seeds
        
        # Update the dp array for possible money values
        for current_money in range(money, crop["Seed Cost"] * max_seeds - 1, -1):
            if dp[current_money - crop["Seed Cost"] * max_seeds] + total_profit > dp[current_money]:
                dp[current_money] = dp[current_money - crop["Seed Cost"] * max_seeds] + total_profit
                crop_combinations[current_money] = crop_combinations[current_money - crop["Seed Cost"] * max_seeds] + [(crop["Name"], max_seeds, crop["Seed Cost"])]
    
    # Find the best possible profit and combination
    max_profit = max(dp)
    best_combination = crop_combinations[dp.index(max_profit)]
    
    return max_profit, best_combination

# Streamlit app
def main():
    st.title("Stardew Valley Crop Profit Maximizer")
    
    # User input for the current day and available money
    season = st.selectbox("Select the Season", ["Spring", "Summer", "Fall"])
    current_day = st.number_input("Enter the Current Day in the Season", min_value=1, max_value=28, value=1)
    money = st.number_input("Enter Available Money (in gold)", min_value=0, value=1000)
    
    # Load the data
    crops = load_crops_data("crops.csv")
    
    # Filter crops based on season
    crops_in_season = crops[crops["Season"] == season]
    
    # Show available crops
    st.write(f"Filtering crops for season: {season}")
    st.write(crops_in_season)
    
    # Find the best combination of crops
    max_profit, best_combination = knapsack(crops_in_season, season, current_day, money)
    
    if best_combination:
        # Prepare data to display
        crop_summary = []
        total_spent = 0
        
        for name, seeds, seed_cost in best_combination:
            total_spent += seeds * seed_cost
            crop_summary.append({"Crop": name, "Seeds": seeds, "Seed Cost": f"{seed_cost}g", "Total Cost": f"{seeds * seed_cost}g"})
        
        crop_summary.append({"Crop": "Total", "Seeds": "", "Seed Cost": "", "Total Cost": f"{total_spent}g"})
        
        # Display crop summary and profit
        crop_df = pd.DataFrame(crop_summary)
        st.write("### Crop Purchase Summary:")
        st.dataframe(crop_df)
        
        result = f"Total Profit: {max_profit}g"
    else:
        result = "No crops can be planted profitably for the remaining days in the season."
    
    # Display result
    st.write(result)

if __name__ == "__main__":
    main()
