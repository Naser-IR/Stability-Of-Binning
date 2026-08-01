# import pandas as pd
# import os

# def bin_and_aggregate_age(file_path, num_bins=5):
#     # 1. Load the dataset
#     print(f"Loading {file_path}...")
#     df = pd.read_csv(file_path)
    
#     # 2. Apply Binning
#     # Equi-width: Equal numerical ranges (e.g., 0-20, 20-40)
#     df['AGE_equi_width'] = pd.cut(df['AGE'], bins=num_bins)
    
#     # Equi-depth: Equal number of records per bin 
#     # (duplicates='drop' is required if many rows share the exact same value)
#     df['AGE_equi_depth'] = pd.qcut(df['AGE'], q=num_bins, duplicates='drop')

#     # 3. Perform Aggregation
#     # We will group by the bins and aggregate both the Record Count and Total Population (RESPOP)
#     print(f"\n--- Equi-Width Aggregation ({num_bins} Bins) ---")
#     width_agg = df.groupby('AGE_equi_width', observed=False).agg(
#         Record_Count=('AGE', 'count'),          # Number of rows in this age bracket
#         # Total_Population=('RESPOP', 'sum')      # Sum of the actual population
#     ).reset_index()
#     print(width_agg.to_string(index=False))

#     print(f"\n--- Equi-Depth Aggregation ({num_bins} Bins) ---")
#     depth_agg = df.groupby('AGE_equi_depth', observed=False).agg(
#         Record_Count=('AGE', 'count'),
#         # Total_Population=('RESPOP', 'sum')
#     ).reset_index()
#     print(depth_agg.to_string(index=False))

# # # Run the function
# # if __name__ == "__main__":
# #     bin_and_aggregate_age("/Users/naserihab/Desktop/state_dataset/MARC2020-County-02.csv", num_bins=5)


###This is the new code that I have added to unroll the census data and then run the main processing loop for changing m and epsilon
import pandas as pd

def unroll_census_data(input_file, output_file, count_column='RESPOP'):
    """
    Reads a CSV and duplicates each row based on the integer value found 
    in the count_column (e.g., RESPOP). Sets the count_column to 1 after unrolling.
    """
    # Check if the input file actually exists before trying to load it
    if not os.path.exists(input_file):
        print(f"Skipping: {input_file} (File not found)")
        return

    print(f"\n--- Processing {input_file} ---")
    df = pd.read_csv(input_file)
    
    original_rows = len(df)
    total_population = df[count_column].sum()
    print(f"Original rows: {original_rows:,}")
    print(f"Expected new rows: {total_population:,}")
    
    print("Expanding rows...")
    expanded_df = df.loc[df.index.repeat(df[count_column])].reset_index(drop=True)
    
    # THE FIX: Set the population column to 1 so aggregations work correctly later
    expanded_df[count_column] = 1 
    
    actual_new_rows = len(expanded_df)
    print(f"Expansion complete! Generated {actual_new_rows:,} rows.")
    
    print(f"Saving to {output_file}...")
    expanded_df.to_csv(output_file, index=False)
    print(f"Success! Saved: {output_file}")


# ==========================================
# Run the Script in a Loop
# ==========================================
# if __name__ == "__main__":
#     # Base directories (Make sure the updated folder exists!)
#     input_dir = "/Users/naserihab/Desktop/state_dataset"
#     output_dir = "/Users/naserihab/Desktop/state_dataset_updated"

#     # Create the output directory if it doesn't exist yet
#     os.makedirs(output_dir, exist_ok=True)

#     # Loop from 1 to 56 (inclusive)
#     for i in range(1, 57):
#         # Format the number to always be 2 digits (e.g., 01, 02, ..., 56)
#         file_num = f"{i:02d}"
        
#         # Construct the file paths dynamically
#         INPUT_CSV = f"{input_dir}/MARC2020-County-{file_num}.csv"
#         OUTPUT_CSV = f"{output_dir}/state_{file_num}.csv"
        
#         # Run the unroll function
#         unroll_census_data(input_file=INPUT_CSV, output_file=OUTPUT_CSV, count_column="RESPOP")
        
#     print("\nAll files have been processed successfully!")






import pandas as pd
import os
import time



from stable_constrain import (
    algorithm2_independent_naive,
    algorithm4_independent_dp,
    algorithm5_independent_graph,
)


# ==========================================
# Helper Functions
# ==========================================
def _timed_call(fn, *args, **kwargs):
    """Run a function and return (result, seconds)."""
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    dt = time.perf_counter() - t0
    return out, dt

def get_boundaries_and_c(df, attr_col, num_bins=10):
    """
    Calculates the total records for 'C', and extracts the inner 
    boundaries for both equi-width and equi-depth.
    """
    total_records = len(df)
    c_value = total_records / 100.0
    
    _, width_edges = pd.cut(df[attr_col], bins=num_bins, retbins=True)
    _, depth_edges = pd.qcut(df[attr_col], q=num_bins, duplicates='drop', retbins=True)
    
    width_required = [round(float(x), 1) for x in width_edges[1:-1]]
    depth_required = [round(float(x), 1) for x in depth_edges[1:-1]]
    
    return c_value, width_required, depth_required

# ==========================================
# Main Processing Loop for changing m
# ==========================================
def main():
    input_dir = "/Users/naserihab/Desktop/state_dataset_updated"
    summary_output_file = "success_percentages_summary.csv"
    
    # --- Algorithm configuration (Static parameters) ---
    ATTR_COL = "AGE"     
    L, U, STEP = 0.0, 100.0, 1.0  
    EPS = 3.0
    USE_PREFILTER = True
    K = 10               
    MIN_WIDTH = 0             
    MAX_WIDTH = 100       # Increased to 100 so Equi-Depth doesn't fail immediately      
    EXCLUDED_BOUNDARIES = None  

    # --- Generate Multipliers (2.5, 2.6, 2.7 ... 3.5) ---
    multipliers = [round(2.5 + i * 0.1, 1) for i in range(11)]
    
    # --- Tracking Dictionary for Success Rates ---
    # We will store the totals and successes for every multiplier
    stats = {m: {"width_success": 0, "width_total": 0, "depth_success": 0, "depth_total": 0} for m in multipliers}

    # Loop through all 56 state files
    for i in range(1, 57):
        file_num = f"{i:02d}"
        CSV_PATH = f"{input_dir}/state_{file_num}.csv"
        
        if not os.path.exists(CSV_PATH):
            continue
            
        print(f"\n{'='*60}")
        print(f"Processing File {file_num}: {os.path.basename(CSV_PATH)}")
        print(f"{'='*60}")
        
        print("Loading data...")
        df = pd.read_csv(CSV_PATH, low_memory=False)
        series = pd.to_numeric(df[ATTR_COL], errors="coerce").dropna()
        
        current_c, req_bounds_width, req_bounds_depth = get_boundaries_and_c(df, ATTR_COL, num_bins=K)
        
        # Test every multiplier on this single file
        for m in multipliers:
            C = current_c * EPS * m
            
            # --- EQUI-WIDTH ---
            stats[m]["width_total"] += 1
            try:
                (cuts5_w, _) = _timed_call(
                    algorithm5_independent_graph, 
                    series, L, U, STEP, K, EPS, C,
                    use_boundary_prefilter=USE_PREFILTER,
                    min_width=MIN_WIDTH,
                    max_width=MAX_WIDTH,
                    excluded_boundaries=EXCLUDED_BOUNDARIES,
                    required_boundaries=req_bounds_width,
                )
                if cuts5_w: 
                    stats[m]["width_success"] += 1
            except Exception:
                pass # Ignoring print statements to keep the loop clean

            # --- EQUI-DEPTH ---
            stats[m]["depth_total"] += 1
            try:
                (cuts5_d, _) = _timed_call(
                    algorithm5_independent_graph, 
                    series, L, U, STEP, K, EPS, C,
                    use_boundary_prefilter=USE_PREFILTER,
                    min_width=MIN_WIDTH,
                    max_width=MAX_WIDTH,
                    excluded_boundaries=EXCLUDED_BOUNDARIES,
                    required_boundaries=req_bounds_depth,
                )
                if cuts5_d:
                    stats[m]["depth_success"] += 1
            except Exception:
                pass

        print(f"Finished testing all {len(multipliers)} multipliers for file {file_num}.")

    # ---------------------------------------------------------
    # Final Summary Calculation & File Save
    # ---------------------------------------------------------
    print(f"\n{'='*60}")
    print("CALCULATING FINAL PERCENTAGES AND SAVING TO CSV")
    print(f"{'='*60}")
    
    # Convert tracking dictionary into a list for pandas
    results_list = []
    
    for m in multipliers:
        w_total = stats[m]["width_total"]
        w_success = stats[m]["width_success"]
        d_total = stats[m]["depth_total"]
        d_success = stats[m]["depth_success"]
        
        w_pct = (w_success / w_total * 100) if w_total > 0 else 0.0
        d_pct = (d_success / d_total * 100) if d_total > 0 else 0.0
        
        results_list.append({
            "C_Multiplier": m,
            "Equi_Width_Total_Runs": w_total,
            "Equi_Width_Successes": w_success,
            "Equi_Width_Success_Pct": round(w_pct, 2),
            "Equi_Depth_Total_Runs": d_total,
            "Equi_Depth_Successes": d_success,
            "Equi_Depth_Success_Pct": round(d_pct, 2)
        })
        
        print(f"Multiplier {m}x -> Width: {w_pct:.2f}% | Depth: {d_pct:.2f}%")
        
    # Save to CSV
    summary_df = pd.DataFrame(results_list)
    summary_df.to_csv(summary_output_file, index=False)
    print(f"\nSuccess! Results saved to '{summary_output_file}'.")

# import os
# import pandas as pd
# Assuming _timed_call, algorithm5_independent_graph, and get_boundaries_and_c are imported here

# ==========================================
# Main Processing Loop for changing m and epsilon
# ==========================================
def main1():
    input_dir = "/Users/naserihab/Desktop/state_dataset_updated"
    summary_output_file = "success_percentages_summary.csv"
    
    # --- Algorithm configuration (Static parameters) ---
    ATTR_COL = "AGE"     
    L, U, STEP = 0.0, 100.0, 1.0  
    USE_PREFILTER = True
    K = 10               
    MIN_WIDTH = 0             
    MAX_WIDTH = 100       # Increased to 100 so Equi-Depth doesn't fail immediately      
    EXCLUDED_BOUNDARIES = None  

    # --- Generate Dynamic Parameters ---
    eps_values = [3.0, 4.0, 5.0, 6.0, 7.0]
    multipliers = [round(2.5 + i * 0.1, 1) for i in range(11)]
    
    # --- Tracking Dictionary for Success Rates ---
    # Key is a tuple: (eps, m)
    stats = {
        (eps, m): {"width_success": 0, "width_total": 0, "depth_success": 0, "depth_total": 0} 
        for eps in eps_values for m in multipliers
    }

    # Loop through all 56 state files
    for i in range(1, 57):
        file_num = f"{i:02d}"
        CSV_PATH = f"{input_dir}/state_{file_num}.csv"
        
        if not os.path.exists(CSV_PATH):
            continue
            
        print(f"\n{'='*60}")
        print(f"Processing File {file_num}: {os.path.basename(CSV_PATH)}")
        print(f"{'='*60}")
        
        print("Loading data...")
        df = pd.read_csv(CSV_PATH, low_memory=False)
        series = pd.to_numeric(df[ATTR_COL], errors="coerce").dropna()
        
        current_c, req_bounds_width, req_bounds_depth = get_boundaries_and_c(df, ATTR_COL, num_bins=K)
        
        # Test every combination of EPS and MULTIPLIER on this single file
        for eps in eps_values:
            print(f"  -> Testing Epsilon: {eps}")
            for m in multipliers:
                C = current_c * eps * m
                
                # --- EQUI-WIDTH ---
                stats[(eps, m)]["width_total"] += 1
                try:
                    (cuts5_w, _) = _timed_call(
                        algorithm5_independent_graph, 
                        series, L, U, STEP, K, eps, C,  # Note: passing eps here instead of static EPS
                        use_boundary_prefilter=USE_PREFILTER,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                        required_boundaries=req_bounds_width,
                    )
                    if cuts5_w: 
                        stats[(eps, m)]["width_success"] += 1
                except Exception:
                    pass 

                # --- EQUI-DEPTH ---
                stats[(eps, m)]["depth_total"] += 1
                try:
                    (cuts5_d, _) = _timed_call(
                        algorithm5_independent_graph, 
                        series, L, U, STEP, K, eps, C,  # Note: passing eps here
                        use_boundary_prefilter=USE_PREFILTER,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                        required_boundaries=req_bounds_depth,
                    )
                    if cuts5_d:
                        stats[(eps, m)]["depth_success"] += 1
                except Exception:
                    pass

        print(f"Finished testing all parameter combinations for file {file_num}.")

    # ---------------------------------------------------------
    # Final Summary Calculation & File Save
    # ---------------------------------------------------------
    print(f"\n{'='*60}")
    print("CALCULATING FINAL PERCENTAGES AND SAVING TO CSV")
    print(f"{'='*60}")
    
    # Convert tracking dictionary into a list for pandas
    results_list = []
    
    for eps in eps_values:
        print(f"\n--- Results for EPS = {eps} ---")
        for m in multipliers:
            w_total = stats[(eps, m)]["width_total"]
            w_success = stats[(eps, m)]["width_success"]
            d_total = stats[(eps, m)]["depth_total"]
            d_success = stats[(eps, m)]["depth_success"]
            
            w_pct = (w_success / w_total * 100) if w_total > 0 else 0.0
            d_pct = (d_success / d_total * 100) if d_total > 0 else 0.0
            
            results_list.append({
                "Epsilon": eps,
                "C_Multiplier": m,
                "Equi_Width_Total_Runs": w_total,
                "Equi_Width_Successes": w_success,
                "Equi_Width_Success_Pct": round(w_pct, 2),
                "Equi_Depth_Total_Runs": d_total,
                "Equi_Depth_Successes": d_success,
                "Equi_Depth_Success_Pct": round(d_pct, 2)
            })
            
            print(f"  Multiplier {m}x -> Width: {w_pct:.2f}% | Depth: {d_pct:.2f}%")
        
    # Save to CSV
    summary_df = pd.DataFrame(results_list)
    # Sort just to guarantee perfect ordering in the output CSV
    summary_df = summary_df.sort_values(by=["Epsilon", "C_Multiplier"]) 
    summary_df.to_csv(summary_output_file, index=False)
    print(f"\nSuccess! Results saved to '{summary_output_file}'.")




def main2():
    input_dir = "/Users/naserihab/Desktop/state_dataset_updated"
    summary_output_file = "success_percentages_summary.csv"
    
    # --- Algorithm configuration (Static parameters) ---
    ATTR_COL = "AGE"     
    L, U, STEP = 0.0, 100.0, 1.0  
    USE_PREFILTER = True
    K = 10               
    MIN_WIDTH = 0             
    MAX_WIDTH = 100             
    EXCLUDED_BOUNDARIES = None  

    # --- Generate Dynamic Parameters ---
    eps_values = [3.0]
    multipliers = [round(2.5 + i * 0.1, 1) for i in range(11)]
    
    # --- Tracking Dictionary for Success Rates ---
    # Added unconstrained tracking metrics
    stats = {
        (eps, m): {
            "width_success": 0, "width_total": 0, 
            "depth_success": 0, "depth_total": 0,
            "unconstrained_success": 0, "unconstrained_total": 0
        } 
        for eps in eps_values for m in multipliers
    }

    # Loop through all 56 state files
    for i in range(1, 57):
        file_num = f"{i:02d}"
        CSV_PATH = f"{input_dir}/state_{file_num}.csv"
        
        if not os.path.exists(CSV_PATH):
            continue
            
        print(f"\n{'='*60}")
        print(f"Processing File {file_num}: {os.path.basename(CSV_PATH)}")
        print(f"{'='*60}")
        
        print("Loading data...")
        df = pd.read_csv(CSV_PATH, low_memory=False)
        series = pd.to_numeric(df[ATTR_COL], errors="coerce").dropna()
        
        current_c, req_bounds_width, req_bounds_depth = get_boundaries_and_c(df, ATTR_COL, num_bins=K)
        
        # Test every combination of EPS and MULTIPLIER on this single file
        for eps in eps_values:
            for m in multipliers:
                C = current_c * eps * m
                
                # 1. --- EQUI-WIDTH ---
                stats[(eps, m)]["width_total"] += 1
                try:
                    (cuts5_w, _) = _timed_call(
                        algorithm5_independent_graph, 
                        series, L, U, STEP, K, eps, C,
                        use_boundary_prefilter=USE_PREFILTER,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                        required_boundaries=req_bounds_width,
                    )
                    if cuts5_w: 
                        stats[(eps, m)]["width_success"] += 1
                except Exception:
                    pass 

                # 2. --- EQUI-DEPTH ---
                stats[(eps, m)]["depth_total"] += 1
                try:
                    (cuts5_d, _) = _timed_call(
                        algorithm5_independent_graph, 
                        series, L, U, STEP, K, eps, C,
                        use_boundary_prefilter=USE_PREFILTER,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                        required_boundaries=req_bounds_depth,
                    )
                    if cuts5_d:
                        stats[(eps, m)]["depth_success"] += 1
                except Exception:
                    pass
                    
                # 3. --- UNCONSTRAINED (Any Stable Cut) ---
                stats[(eps, m)]["unconstrained_total"] += 1
                try:
                    (cuts5_u, _) = _timed_call(
                        algorithm5_independent_graph, 
                        series, L, U, STEP, K, eps, C,
                        use_boundary_prefilter=USE_PREFILTER,
                        min_width=MIN_WIDTH,
                        max_width=MAX_WIDTH,
                        excluded_boundaries=EXCLUDED_BOUNDARIES,
                        required_boundaries=None,  # <--- NO REQUIRED BOUNDARIES
                    )
                    if cuts5_u:
                        stats[(eps, m)]["unconstrained_success"] += 1
                except Exception:
                    pass

        print(f"Finished testing all parameter combinations for file {file_num}.")

    # ---------------------------------------------------------
    # Final Summary Calculation & File Save
    # ---------------------------------------------------------
    print(f"\n{'='*60}")
    print("CALCULATING FINAL PERCENTAGES AND SAVING TO CSV")
    print(f"{'='*60}")
    
    results_list = []
    
    for eps in eps_values:
        print(f"\n--- Results for EPS = {eps} ---")
        for m in multipliers:
            w_total = stats[(eps, m)]["width_total"]
            w_success = stats[(eps, m)]["width_success"]
            
            d_total = stats[(eps, m)]["depth_total"]
            d_success = stats[(eps, m)]["depth_success"]
            
            u_total = stats[(eps, m)]["unconstrained_total"]
            u_success = stats[(eps, m)]["unconstrained_success"]
            
            w_pct = (w_success / w_total * 100) if w_total > 0 else 0.0
            d_pct = (d_success / d_total * 100) if d_total > 0 else 0.0
            u_pct = (u_success / u_total * 100) if u_total > 0 else 0.0
            
            results_list.append({
                "Epsilon": eps,
                "C_Multiplier": m,
                "Equi_Width_Total": w_total,
                "Equi_Width_Successes": w_success,
                "Equi_Width_Success_Pct": round(w_pct, 2),
                "Equi_Depth_Total": d_total,
                "Equi_Depth_Successes": d_success,
                "Equi_Depth_Success_Pct": round(d_pct, 2),
                "Unconstrained_Total": u_total,
                "Unconstrained_Successes": u_success,
                "Unconstrained_Success_Pct": round(u_pct, 2)
            })
            
            print(f"  Multiplier {m}x -> Width: {w_pct:.1f}% | Depth: {d_pct:.1f}% | Unconstrained: {u_pct:.1f}%")
        
    # Save to CSV
    summary_df = pd.DataFrame(results_list)
    summary_df = summary_df.sort_values(by=["Epsilon", "C_Multiplier"]) 
    summary_df.to_csv(summary_output_file, index=False)
    print(f"\nSuccess! Results saved to '{summary_output_file}'.")


if __name__ == "__main__":
    main2()



# # ==========================================
# # Helper Functions
# # ==========================================
# def _timed_call(fn, *args, **kwargs):
#     """Run a function and return (result, seconds)."""
#     t0 = time.perf_counter()
#     out = fn(*args, **kwargs)
#     dt = time.perf_counter() - t0
#     return out, dt

# def get_boundaries_and_c(df, attr_col, num_bins=10):
#     """
#     Calculates the total records for 'C', and extracts the inner 
#     boundaries for both equi-width and equi-depth from an existing DataFrame.
#     """
#     # Calculate C: Total records divided by 100
#     total_records = len(df)
#     c_value = total_records / 100.0
    
#     # Get Equi-Width boundaries
#     _, width_edges = pd.cut(df[attr_col], bins=num_bins, retbins=True)
    
#     # Get Equi-Depth boundaries
#     _, depth_edges = pd.qcut(df[attr_col], q=num_bins, duplicates='drop', retbins=True)
    
#     # Extract only the inner boundaries (ignore the min and max edges like 0 and 100)
#     width_required = [round(float(x), 1) for x in width_edges[1:-1]]
#     depth_required = [round(float(x), 1) for x in depth_edges[1:-1]]
    
#     return c_value, width_required, depth_required

# # ==========================================
# # Main Processing Loop
# # ==========================================
# def main():
#     input_dir = "/Users/naserihab/Desktop/state_dataset_updated"
    
#     # --- Algorithm configuration (Static parameters) ---
#     ATTR_COL = "AGE"     
#     L, U, STEP = 0.0, 100.0, 1.0  
#     EPS = 1.0
#     USE_PREFILTER = True
#     K = 10               # Must match num_bins
#     MIN_WIDTH = 0             
#     MAX_WIDTH = 100             
#     EXCLUDED_BOUNDARIES = None  

#     # --- TRACKING VARIABLES FOR SUCCESS RATE ---
#     width_total_runs = 0
#     width_success_runs = 0
    
#     depth_total_runs = 0
#     depth_success_runs = 0

    
#     # Loop through all 56 state files
#     for i in range(1, 57):
#         file_num = f"{i:02d}"
#         CSV_PATH = f"{input_dir}/state_{file_num}.csv"
        
#         if not os.path.exists(CSV_PATH):
#             print(f"\nSkipping File {file_num}, file not found.")
#             continue
            
#         print(f"\n{'='*60}")
#         print(f"Processing File {file_num}: {os.path.basename(CSV_PATH)}")
#         print(f"{'='*60}")
        
#         # 1. Load data once per file
#         print(f"Loading data...")
#         df = pd.read_csv(CSV_PATH, low_memory=False)
#         series = pd.to_numeric(df[ATTR_COL], errors="coerce").dropna()
        
#         # 2. Extract dynamic variables for this specific file
#         current_c, req_bounds_width, req_bounds_depth = get_boundaries_and_c(df, ATTR_COL, num_bins=K)
#         C = current_c * EPS * 2.5
        
#         # ---------------------------------------------------------
#         # Run Algorithm 5 for EQUI-WIDTH
#         # ---------------------------------------------------------
#         print("\n--- Algorithm 5 (Graph/DFS) - EQUI-WIDTH ---")
#         REQUIRED_BOUNDARIES = req_bounds_width
        
#         print(f"Constraints Active:")
#         print(f"  - K (Bins):  {K}")
#         print(f"  - C Value:   {C}")
#         print(f"  - Required:  {REQUIRED_BOUNDARIES}")
        
#         width_total_runs += 1
#         try:
#             (cuts5_w, t5_w) = _timed_call(
#                 algorithm5_independent_graph, 
#                 series, L, U, STEP, K, EPS, C,
#                 use_boundary_prefilter=USE_PREFILTER,
#                 min_width=MIN_WIDTH,
#                 max_width=MAX_WIDTH,
#                 excluded_boundaries=EXCLUDED_BOUNDARIES,
#                 required_boundaries=REQUIRED_BOUNDARIES,
#             )
#             print(f"Time Taken: {t5_w:.6f} seconds")
#             print(f"Stable Cuts Found: {cuts5_w}")
            
#             # Check if it actually returned valid cuts (not None and not empty)
#             if cuts5_w: 
#                 width_success_runs += 1
                
#         except Exception as e:
#             print(f"Error (Equi-Width): {repr(e)}")

#         # ---------------------------------------------------------
#         # Run Algorithm 5 for EQUI-DEPTH
#         # ---------------------------------------------------------
#         print("\n--- Algorithm 5 (Graph/DFS) - EQUI-DEPTH ---")
#         REQUIRED_BOUNDARIES = req_bounds_depth
        
#         print(f"Constraints Active:")
#         print(f"  - K (Bins):  {K}")
#         print(f"  - C Value:   {C}")
#         print(f"  - Required:  {REQUIRED_BOUNDARIES}")
        
#         depth_total_runs += 1
#         try:
#             (cuts5_d, t5_d) = _timed_call(
#                 algorithm5_independent_graph, 
#                 series, L, U, STEP, K, EPS, C,
#                 use_boundary_prefilter=USE_PREFILTER,
#                 min_width=MIN_WIDTH,
#                 max_width=MAX_WIDTH,
#                 excluded_boundaries=EXCLUDED_BOUNDARIES,
#                 required_boundaries=REQUIRED_BOUNDARIES,
#             )
#             print(f"Time Taken: {t5_d:.6f} seconds")
#             print(f"Stable Cuts Found: {cuts5_d}")
            
#             # Check if it actually returned valid cuts (not None and not empty)
#             if cuts5_d:
#                 depth_success_runs += 1
                
#         except Exception as e:
#             print(f"Error (Equi-Depth): {repr(e)}")

#     # ---------------------------------------------------------
#     # Final Success Summary
#     # ---------------------------------------------------------
#     print(f"\n{'='*60}")
#     print("FINAL SUMMARY REPORT: STABLE CUTS PERCENTAGE")
#     print(f"{'='*60}")
    
#     if width_total_runs > 0:
#         width_pct = (width_success_runs / width_total_runs) * 100
#         print(f"Equi-Width Success Rate: {width_pct:.2f}%  ({width_success_runs} successes / {width_total_runs} attempts)")
#     else:
#         print("Equi-Width Success Rate: N/A (0 files processed)")
        
#     if depth_total_runs > 0:
#         depth_pct = (depth_success_runs / depth_total_runs) * 100
#         print(f"Equi-Depth Success Rate: {depth_pct:.2f}%  ({depth_success_runs} successes / {depth_total_runs} attempts)")
#     else:
#         print("Equi-Depth Success Rate: N/A (0 files processed)")
    
#     print(f"{'='*60}\n")


# if __name__ == "__main__":
#     # Note: Make sure algorithm5_independent_graph is imported or defined above this script
#     main()