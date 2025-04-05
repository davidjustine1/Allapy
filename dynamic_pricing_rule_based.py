# Recommended for Mini-Project Deadline

import datetime

def calculate_price_with_rules(base_price_per_night, check_in_date_str, check_out_date_str, platform_fee_percent=10.0):
    """
    Calculates the total price for a stay based on simple rules 
    (season, weekend) and adds a platform fee. This is the recommended
    approach for the mini-project given time constraints.

    Args:
        base_price_per_night (float): The owner's base price for the boat per night.
        check_in_date_str (str): Check-in date as 'YYYY-MM-DD'. Can come from user input.
        check_out_date_str (str): Check-out date as 'YYYY-MM-DD'. Can come from user input.
        platform_fee_percent (float): Platform fee as a percentage (e.g., 10 for 10%).

    Returns:
        float: The total calculated final price for the stay, including fees.
               Returns None if dates are invalid or check_out is not after check_in.
    """
    # Input validation
    if not all([base_price_per_night, check_in_date_str, check_out_date_str]):
         print("Error: Missing required price or date inputs.")
         return None
         
    try:
        # Convert string dates to date objects
        check_in_date = datetime.date.fromisoformat(check_in_date_str)
        check_out_date = datetime.date.fromisoformat(check_out_date_str)
        
        # Basic date validity check
        if check_out_date <= check_in_date:
            print("Error: Check-out date must be after check-in date.")
            return None 

        num_nights = (check_out_date - check_in_date).days
        total_rule_based_price = 0
        current_date = check_in_date

        # Calculate price night by night applying rules
        for _ in range(num_nights):
            nightly_price = float(base_price_per_night) # Ensure base price is float
            month = current_date.month
            weekday = current_date.weekday() # Monday is 0, Sunday is 6

            # --- Rule 1: Seasonality ---
            season_multiplier = 1.0 # Default multiplier
            if month in [12, 1, 2]: # Dec, Jan, Feb - Peak Season (~20% markup)
                season_multiplier = 1.20 
            elif month in [6, 7, 8]: # Jun, Jul, Aug - Monsoon/Off-peak (~15% discount)
                season_multiplier = 0.85 
            
            # --- Rule 2: Weekends ---
            weekend_multiplier = 1.0 # Default multiplier
            # Apply markup if the *night being booked* is Friday (4) or Saturday (5)
            if weekday in [4, 5]: 
                weekend_multiplier = 1.15 # ~15% markup

            # Apply multipliers for the current night
            nightly_price *= season_multiplier * weekend_multiplier
            total_rule_based_price += nightly_price

            # Move calculation to the next day
            current_date += datetime.timedelta(days=1)

        # --- Rule 3: Platform Fee ---
        # Apply fee AFTER calculating the dynamic base price
        final_display_price = total_rule_based_price * (1 + (platform_fee_percent / 100.0))

        # Return the final price rounded to 2 decimal places
        return round(final_display_price, 2) 

    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        return None
    except Exception as e:
        print(f"Error during rule-based price calculation: {e}")
        return None

# --- Example of how to use this function in Flask ---
if __name__ == "__main__":
    # This part only runs when the script is executed directly
    print("--- Rule-Based Dynamic Pricing Example ---")
    
    # Example inputs (these would come from DB and user request in Flask)
    base = 7000.0
    check_in = '2024-12-20' # Peak Season Friday
    check_out = '2024-12-22' # Booking Fri night, Sat night (2 nights)
    fee = 10.0

    # Call the function
    total_price = calculate_price_with_rules(base, check_in, check_out, fee)

    # Display result
    if total_price is not None:
        print(f"  Base Price/Night: ₹{base:.2f}")
        print(f"  Check-in: {check_in}, Check-out: {check_out}")
        print(f"  Platform Fee: {fee}%")
        print(f"  Calculated Total Price: ₹{total_price:.2f}") 
        # Expected: Night 1 (Fri, Peak): 7000*1.2*1.15 = 9660
        #           Night 2 (Sat, Peak): 7000*1.2*1.15 = 9660
        #           Total before fee: 19320
        #           Total after 10% fee: 19320 * 1.10 = 21252.00
    else:
        print("  Could not calculate price due to errors.")

    # Example 2: Off-season weekday
    check_in_off = '2024-07-10' # Off-Season Wednesday
    check_out_off = '2024-07-11' # 1 night
    total_price_off = calculate_price_with_rules(base, check_in_off, check_out_off, fee)
    if total_price_off is not None:
         print(f"\n  Off-Season Weekday Example:")
         print(f"  Calculated Total Price: ₹{total_price_off:.2f}")
         # Expected: Night 1 (Wed, Off): 7000*0.85*1.0 = 5950
         #           Total before fee: 5950
         #           Total after 10% fee: 5950 * 1.10 = 6545.00