import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter
from itertools import combinations

def analyze_incident_trend(df: pd.DataFrame):
    """
    Analyzes and plots the Year-over-Year trend of UNIQUE incidents.
    
    Args:
        df: The unpivoted DataFrame where each row is an offense, but includes
        incident-level identifiers like 'incident_number', and 'year'.
    """
    if 'year' not in df.columns or 'incident_number' not in df.columns:
        print("Error: DataFrame is missing required columns ('year', 'incident_number').")
        return

    # Group by year and count the number of UNIQUE incident IDs
    yearly_incidents = (
        df.groupby('year')['incident_number']
        .nunique()
        .sort_index()
    )

    if yearly_incidents.empty:
        print("No incident data available for trend analysis.")
        return

    # --- Plotting and Visualization ---
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))

    # Create line chart
    ax.plot(yearly_incidents.index, yearly_incidents.values, marker='o', 
            color='#FF6B35', linewidth=3, markersize=8, 
            markerfacecolor='white', markeredgecolor='#FF6B35', markeredgewidth=2)

    # Add value labels on each point
    for i, (year, count) in enumerate(yearly_incidents.items()):
        y_offset = yearly_incidents.max() * 0.02 
        ax.text(year, count + y_offset, f'{count:,}', ha='center', va='bottom', 
                fontsize=15, fontweight='bold', color='#FF6B35')

    # Calculate year-over-year change
    yoy_change = yearly_incidents.pct_change() * 100

    # Add YoY change annotations
    if len(yearly_incidents) > 1:
        for i in range(1, len(yearly_incidents)):
            prev_year = yearly_incidents.index[i-1]
            curr_year = yearly_incidents.index[i]
            change_pct = yoy_change.iloc[i]
            
            mid_x = (prev_year + curr_year) / 2
            mid_y = (yearly_incidents.iloc[i-1] + yearly_incidents.iloc[i]) / 2
            
            color = 'green' if change_pct >= 0 else 'red'
            sign = '+' if change_pct >= 0 else ''
            
            ax.annotate(f'{sign}{change_pct:.1f}%', 
                        xy=(mid_x, mid_y), 
                        xytext=(0, 20), textcoords='offset points',
                        ha='center', va='bottom', fontsize=12, fontweight='bold', 
                        color=color, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    # Final plot styling
    ax.set_xlabel('Year', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Unique Hate Crime Incidents', fontsize=14, fontweight='bold')
    ax.set_title('Year-over-Year Hate Crime Incident Trend', fontsize=16, fontweight='bold', pad=20)
    ax.set_xticks(yearly_incidents.index)
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, yearly_incidents.max() * 1.25) 

    plt.tight_layout()
    plt.show()

    # --- Console Output ---
    print("\n📈 YEAR-OVER-YEAR TREND ANALYSIS (Unique Incidents):")
    print("="*60)
    for year, count in yearly_incidents.items():
        print(f"   • {year}: {count:,} unique incidents")

    print(f"\n📊 TREND INSIGHTS:")
    if not yearly_incidents.empty and len(yearly_incidents) > 1:
        initial_count = yearly_incidents.iloc[0]
        final_count = yearly_incidents.iloc[-1]
        
        total_growth_pct = 0
        if initial_count > 0:
            total_growth_pct = ((final_count / initial_count) - 1) * 100
        
        print(f"   • Total Growth: {final_count - initial_count:+,} incidents "
              f"({total_growth_pct:+.1f}%) across the period.")
        print(f"   • Peak Year: {yearly_incidents.idxmax()} ({yearly_incidents.max():,} incidents)")
        print(f"   • Lowest Year: {yearly_incidents.idxmin()} ({yearly_incidents.min():,} incidents)")
        
        avg_yoy_change = yoy_change.mean()
        print(f"   • Average YoY Change: {avg_yoy_change:+.1f}%")
        print("\n💡 This trend shows the evolving landscape of hate crimes over time!")
    else:
        print("   • Insufficient data points for YoY analysis.")

def analyze_geographic_trend(df: pd.DataFrame):
    """
    Analyzes and plots the geographic distribution of UNIQUE incidents 
    from the unpivoted DataFrame.

    """
    required_cols = ['incident_number', 'country_region', 'state_name']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: DataFrame is missing required columns for geographic analysis: {required_cols}")
        return

    # Helper function to group and count unique incidents
    def count_unique_incidents(grouping_col):
        # Group by the geographic column and count the number of UNIQUE incident IDs
        counts = (
            df.groupby(grouping_col)['incident_number']
            .nunique()
            .sort_values(ascending=False)
        )
        return counts

    # --------------------------------------------------------------------------
    # Geographic Analysis Plotting
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Regional distribution
    regional = count_unique_incidents('country_region')

    if not regional.empty:
        # Sort ascending for cleaner horizontal bar chart presentation
        regional_sorted = regional.sort_values(ascending=True) 
        
        # Plotting
        axes[0].barh(range(len(regional_sorted)), regional_sorted.values, 
                     color=plt.cm.Oranges(np.linspace(0.9, 0.4, len(regional_sorted))))
        axes[0].set_yticks(range(len(regional_sorted)))
        axes[0].set_yticklabels(regional_sorted.index, fontsize=11)
        axes[0].set_xlabel('Number of Unique Incidents', fontsize=12, fontweight='bold')
        axes[0].set_title('Hate Crimes by Region (Unique Incidents)', fontsize=13, fontweight='bold')
        axes[0].invert_yaxis()
        axes[0].set_xlim(0, regional_sorted.max() * 1.3)
        
        regional_sum = regional_sorted.sum()
        for i, (region, count) in enumerate(regional_sorted.items()):
            pct = count / regional_sum * 100
            axes[0].text(count + regional_sorted.max() * 0.05, i, f'{count:,} ({pct:.1f}%)', 
                         va='center', fontweight='bold', fontsize=10)
    else:
        axes[0].text(0.5, 0.5, 'Region data not available\nin processed dataset', 
                     ha='center', va='center', transform=axes[0].transAxes, fontsize=12)
        axes[0].set_title('Regional Analysis (Data Unavailable)', fontsize=13, fontweight='bold')


    # Top 15 States
    top_states = count_unique_incidents('state_name').head(15)

    if not top_states.empty:
        # Sort ascending for cleaner horizontal bar chart presentation
        top_states_sorted = top_states.sort_values(ascending=True) 

        # Plotting
        axes[1].barh(range(len(top_states_sorted)), top_states_sorted.values, 
                     color=plt.cm.Oranges(np.linspace(0.9, 0.4, len(top_states_sorted))))
        axes[1].set_yticks(range(len(top_states_sorted)))
        axes[1].set_yticklabels(top_states_sorted.index, fontsize=10)
        axes[1].set_xlabel('Number of Unique Incidents', fontsize=12, fontweight='bold')
        axes[1].set_title('Top 15 States by Unique Hate Crime Incidents', fontsize=13, fontweight='bold')
        axes[1].invert_yaxis()
        
        for i, (state, count) in enumerate(top_states_sorted.items()):
            axes[1].text(count + top_states_sorted.max() * 0.03, i, f'{count:,}', va='center', fontsize=9, fontweight='bold')
    else:
        axes[1].text(0.5, 0.5, 'State data not available\nin processed dataset', 
                     ha='center', va='center', transform=axes[1].transAxes, fontsize=12)
        axes[1].set_title('State Analysis (Data Unavailable)', fontsize=13, fontweight='bold')


    plt.tight_layout()
    plt.show()

    # --- Console Output ---
    print("\n🗺️ GEOGRAPHIC INSIGHTS (Unique Incidents):")
    print("="*50)
    
    if not regional.empty:
        # Use the original (descending) regional series for max calculation
        print(f"   • Most Affected Region: {regional.idxmax()} ({regional.max():,} unique incidents)")
    else:
         print("   • Regional data is empty or unavailable.")
         
    if not top_states.empty:
        # Use the original (descending) top_states series for max calculation
        print(f"   • Most Affected State: {top_states.idxmax()} ({top_states.max():,} unique incidents)")
        print(f"   • States Covered: {df['state_name'].nunique()}")
    else:
         print("   • State data is empty or unavailable.")
         
    print("\n💡 Geographic standardization and unique counting ensure meaningful comparisons!")

def analyze_population_rate(df: pd.DataFrame):
    """
    Calculates and plots hate crime incidents per 100,000 population by state.
    
    METHODOLOGY:
    - Numerator: Count of UNIQUE incidents per state.
    - Denominator: 'state_population' (Census/Total state pop), not agency population.
    """
    
    required_cols = ['incident_number', 'state_name', 'state_population']
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        print(f"Error: DataFrame is missing required columns for rate analysis: {missing}")
        return

    # Step 1: Count unique incidents per state
    state_incidents = (
        df.groupby('state_name')['incident_number']
        .nunique()
        .reset_index(name='incidents')
    )

    # Step 2: Aggregate population data per state
    # Since 'state_population' is the total census population repeated on every row 
    # for that state, we take the max() (or first()) to get the single correct value.
    state_population_agg = (
        df.groupby('state_name')['state_population']
        .max() 
        .reset_index(name='state_population')
    )

    # Step 3: Merge the incident counts and population data
    state_pop_data = state_incidents.merge(
        state_population_agg, 
        on='state_name', 
        how='left'
    )

    # Filter out records where population is missing or zero (cannot calculate rate)
    state_pop_data = state_pop_data[
        (state_pop_data['state_population'].notna()) & 
        (state_pop_data['state_population'] > 0)
    ].copy()

    # --------------------------------------------------------------------------
    # Rate Calculation and Sorting
    # --------------------------------------------------------------------------
    # Formula: (Incidents / Total State Population) * 100,000
    state_pop_data['incidents_per_100k'] = (
        state_pop_data['incidents'] / state_pop_data['state_population']
    ) * 100000
    
    # Sort the final data frame
    state_pop_data_sorted = state_pop_data.sort_values('incidents_per_100k', ascending=False)

    # --- Plotting ---
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    # Get Top 10 lists
    top10_count = state_pop_data.nlargest(10, 'incidents').sort_values('incidents', ascending=True)
    top10_rate = state_pop_data.nlargest(10, 'incidents_per_100k').sort_values('incidents_per_100k', ascending=True)

    # --- CHART 1: RAW INCIDENT COUNT ---
    axes[0].barh(range(len(top10_count)), top10_count['incidents'].values,
                 color=plt.cm.Blues(np.linspace(0.9, 0.4, len(top10_count))))
    axes[0].set_yticks(range(len(top10_count)))
    axes[0].set_yticklabels(top10_count['state_name'], fontsize=12)
    axes[0].set_xlabel('Total Unique Incidents', fontweight='bold', fontsize=11)
    axes[0].set_title('Top 10 States: Raw Incident Count (Unique)', fontsize=13, fontweight='bold')
    axes[0].set_xlim(0, top10_count['incidents'].max() * 1.2)
    
    for i, v in enumerate(top10_count['incidents'].values):
        is_max = (v == top10_count['incidents'].max())
        axes[0].text(v + top10_count['incidents'].max() * 0.02, i, f'{v:,.0f}', va='center', fontsize=10, 
                     fontweight='bold' if is_max else 'normal', color=plt.cm.Blues(0.9) if is_max else 'black')

    # --- CHART 2: PER CAPITA RATE (Incidents per 100k) ---
    axes[1].barh(range(len(top10_rate)), top10_rate['incidents_per_100k'].values,
                 color=plt.cm.Oranges(np.linspace(0.9, 0.4, len(top10_rate))))
    axes[1].set_yticks(range(len(top10_rate)))
    axes[1].set_yticklabels(top10_rate['state_name'], fontsize=12)
    axes[1].set_xlabel('Incidents per 100,000 Population', fontweight='bold', fontsize=11)
    axes[1].set_title('Top 10 States: Population-Adjusted Rate', fontsize=13, fontweight='bold')
    axes[1].set_xlim(0, top10_rate['incidents_per_100k'].max() * 1.2)
    
    for i, v in enumerate(top10_rate['incidents_per_100k'].values):
        is_max = (v == top10_rate['incidents_per_100k'].max())
        axes[1].text(v + top10_rate['incidents_per_100k'].max() * 0.02, i, f'{v:.1f}', va='center', fontsize=10, 
                     fontweight='bold' if is_max else 'normal', color=plt.cm.Oranges(0.9) if is_max else 'black')

    plt.tight_layout()
    plt.show()

    # --- Console Output ---
    print("\n📊 POPULATION-ADJUSTED ANALYSIS:")
    print("="*50)
    
    if not state_pop_data_sorted.empty:
        highest_rate_state = state_pop_data_sorted.iloc[0]
        # Recalculate highest count from the full sorted list to ensure accuracy
        highest_count_state = state_pop_data.sort_values('incidents', ascending=False).iloc[0]
        
        print(f"   • Highest Raw Count: {highest_count_state['state_name']} "
              f"({highest_count_state['incidents']:,.0f} unique incidents)")
        print(f"   • Highest Per Capita Rate: {highest_rate_state['state_name']} "
              f"({highest_rate_state['incidents_per_100k']:.1f} per 100k)")
        print(f"   • Average Rate (Across States): {state_pop_data['incidents_per_100k'].mean():.1f} per 100k")
    else:
        print("   • Insufficient data to calculate population-adjusted rates.")
    
    print("\n💡 Raw counts can be MISLEADING - population-adjusted rates show TRUE impact!")
    print("NOTE: This analysis uses 'state_population' (Census data) as the denominator.")

def plot_state_pop_heatmap(df: pd.DataFrame):
    """
    Generates an interactive side-by-side choropleth map comparing:
    1. Raw Incident Counts (Unique Incidents)
    2. Incidents per 100,000 Population
    
    Args:
        df: Unpivoted DataFrame containing 'ori', 'incident_number', 'state_name', 
            and 'state_population'.
    """
    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    
    # Ensure unique incident ID exists
    if 'unique_incident_id' not in df.columns:
        df['unique_incident_id'] = df['ori'].astype(str) + '-' + df['incident_number'].astype(str)
        
    # Count unique incidents per state
    state_incidents = (
        df.groupby('state_name')['unique_incident_id']
        .nunique()
        .reset_index(name='incidents')
    )

    # Aggregate state population (using max to get single reliable value per state)
    state_population_agg = (
        df.groupby('state_name')['state_population']
        .max()
        .reset_index(name='state_population')
    )

    # Merge incidents and population
    state_pop_data = state_incidents.merge(
        state_population_agg, 
        on='state_name', 
        how='left'
    )
    
    # Filter for valid population data to calculate rates
    # (Keeps rows only if we have both incidents and population data)
    state_pop_data = state_pop_data[
        (state_pop_data['state_population'].notna()) & 
        (state_pop_data['state_population'] > 0)
    ].copy()

    # Calculate Rate
    state_pop_data['incidents_per_100k'] = (
        state_pop_data['incidents'] / state_pop_data['state_population']
    ) * 100000

    # -------------------------------------------------------------------------
    # 2. State Code Mapping (Expanded for Territories)
    # -------------------------------------------------------------------------
    state_abbrev = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'District of Columbia': 'DC', 'Puerto Rico': 'PR', 'Guam': 'GU', 'Virgin Islands': 'VI',
        'American Samoa': 'AS', 'Northern Mariana Islands': 'MP'
    }

    state_pop_data['state_code'] = state_pop_data['state_name'].map(state_abbrev)

    # Check for unmapped states (debug step)
    missing_codes = state_pop_data[state_pop_data['state_code'].isna()]['state_name'].unique()
    if len(missing_codes) > 0:
        print(f"⚠️ Warning: The following locations could not be mapped to a state code: {missing_codes}")

    # -------------------------------------------------------------------------
    # 3. Plotly Visualization
    # -------------------------------------------------------------------------
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('<b>Total Incidents (Raw Count)</b>', 
                       '<b>Incidents per 100,000 Population (Rate)</b>'),
        specs=[[{'type': 'choropleth'}, {'type': 'choropleth'}]],
        horizontal_spacing=0.05
    )

    # Map 1: Raw incident counts
    fig.add_trace(
        go.Choropleth(
            locations=state_pop_data['state_code'],
            z=state_pop_data['incidents'],
            locationmode='USA-states',
            colorscale='Blues',
            text=state_pop_data['state_name'],
            hovertemplate='<b>%{text}</b><br>' +
                          'Total Incidents: %{z:,}<br>' +
                          '<extra></extra>',
            colorbar=dict(
                title="Total<br>Incidents",
                x=0.45,
                thickness=15,
                len=0.7
            ),
            marker_line_color='white',
            marker_line_width=1
        ),
        row=1, col=1
    )

    # Map 2: Per capita rates
    fig.add_trace(
        go.Choropleth(
            locations=state_pop_data['state_code'],
            z=state_pop_data['incidents_per_100k'],
            locationmode='USA-states',
            colorscale='Reds',
            text=state_pop_data['state_name'],
            hovertemplate='<b>%{text}</b><br>' +
                          'Rate: %{z:.2f} per 100k<br>' +
                          'Total: ' + state_pop_data['incidents'].apply(lambda x: f'{x:,}') + '<br>' +
                          '<extra></extra>',
            colorbar=dict(
                title="Incidents<br>per 100k",
                x=1.0,
                thickness=15,
                len=0.7
            ),
            marker_line_color='white',
            marker_line_width=1
        ),
        row=1, col=2
    )

    # Update geo layout
    fig.update_geos(
        scope='usa',
        projection_type='albers usa',
        showlakes=True,
        lakecolor='rgb(230, 240, 255)',
        bgcolor='rgba(0,0,0,0)'
    )

    fig.update_layout(
        title={
            'text': '<b>USA Hate Crime Comparison: Raw vs Population-Adjusted</b><br>' +
                    '<sub>Comparing Total Volume vs. Per Capita Impact</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        height=600,
        margin=dict(l=20, r=20, t=100, b=20),
        showlegend=False
    )

    return fig

def plot_region_pop_heatmap(df: pd.DataFrame):
    """
    Generates a static heatmap showing the number of unique incidents 
    by Country Region and Population Group.
    
    Includes hierarchical x-axis labeling for Cities, MSA Counties, and Non-MSA Counties.
    """
    # -------------------------------------------------------------------------
    # 1. Data Aggregation (Unique Incidents)
    # -------------------------------------------------------------------------

    # Group by Region and Population Group, counting UNIQUE incidents
    grouped = (
        df.groupby(['country_region', 'population_group'])['incident_number']
        .nunique()
        .reset_index(name='incidents')
    )

    # Filter out 'Possessions' or 'U.S. Territories' if not desired
    grouped = grouped[~grouped['country_region'].isin(['Possessions', 'U.S. Territories'])]

    # Pivot data
    pivot_table = grouped.pivot(
        index='country_region', 
        columns='population_group', 
        values='incidents'
    ).fillna(0)

    # -------------------------------------------------------------------------
    # 2. Sort Columns Logic (Critical for Hierarchical Labels)
    # -------------------------------------------------------------------------
    # Define the desired column order groups
    cities_cols = [
        'Cities: 1,000,000+', 'Cities: 500,000-999,999', 'Cities: 100,000-499,999', 
        'Cities: 50,000-99,999', 'Cities: 10,000-49,999', 'Cities: under 10,000'
    ]
    msa_cols = ['MSA Counties: 100,000+', 'MSA Counties: 10,000-99,999']
    non_msa_cols = ['Non-MSA Counties: 100,000+', 'Non-MSA Counties: 10,000-99,999']
    
    desired_order = cities_cols + msa_cols + non_msa_cols
    
    # Filter desired order to only include columns that actually exist in the data
    final_order = [col for col in desired_order if col in pivot_table.columns]
    
    # Reindex the pivot table to enforce this order
    pivot_table = pivot_table.reindex(columns=final_order)

    # -------------------------------------------------------------------------
    # 3. Plotting
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(16, 8))
    
    sns.heatmap(pivot_table, annot=True, fmt=",.0f", cmap="Oranges", linewidths=0.5, 
                cbar_kws={'label': 'Number of Unique Incidents'}, ax=ax)

    # Titles and basic labels
    ax.set_title('Heatmap of Unique Incidents by Region and Population Group', fontsize=16, fontweight='bold', pad=45)
    ax.set_xlabel('')  # Remove default xlabel
    ax.set_ylabel('Country Region', fontsize=12, fontweight='bold')

    # -------------------------------------------------------------------------
    # 4. Hierarchical Axis Labeling
    # -------------------------------------------------------------------------
    # Extract just the population ranges (removing "Cities: ", "MSA Counties: ", etc.)
    pop_ranges = []
    for col in final_order:
        if ': ' in col:
            pop_ranges.append(col.split(': ')[1])
        else:
            pop_ranges.append(col) # Fallback if format is different

    # Set bottom ticks (Population Ranges)
    ax.set_xticks(np.arange(len(pop_ranges)) + 0.5)
    ax.set_xticklabels(pop_ranges, rotation=45, ha='right', fontsize=9)

    # Calculate positions for the top-level group labels (Cities, MSA, Non-MSA)
    # We count how many columns from each group actually exist in the final table
    n_cities = sum(1 for c in cities_cols if c in final_order)
    n_msa = sum(1 for c in msa_cols if c in final_order)
    n_non_msa = sum(1 for c in non_msa_cols if c in final_order)

    current_pos = 0
    
    # Add "Cities" label and separator if cities exist
    if n_cities > 0:
        center = current_pos + n_cities / 2
        ax.text(center, -0.2, 'Cities', ha='center', va='top', fontsize=13, fontweight='bold',
                transform=ax.get_xaxis_transform())
        current_pos += n_cities
        # Draw separator
        if current_pos < len(final_order):
            ax.axvline(x=current_pos, color='red', linewidth=2.5, linestyle='-')

    # Add "MSA Counties" label and separator if MSAs exist
    if n_msa > 0:
        center = current_pos + n_msa / 2
        ax.text(center, -0.2, 'MSA Counties', ha='center', va='top', fontsize=13, fontweight='bold',
                transform=ax.get_xaxis_transform())
        current_pos += n_msa
        # Draw separator
        if current_pos < len(final_order):
            ax.axvline(x=current_pos, color='red', linewidth=2.5, linestyle='-')

    # Add "Non-MSA Counties" label
    if n_non_msa > 0:
        center = current_pos + n_non_msa / 2
        ax.text(center, -0.2, 'Non-MSA Counties', ha='center', va='top', fontsize=13, fontweight='bold',
                transform=ax.get_xaxis_transform())

    plt.tight_layout()
    plt.show()

    # Print summary (excluding Possessions)
    grouped_filtered = grouped[grouped['country_region'] != 'Possessions']
    print("\n📊 INCIDENTS BY COUNTRY REGION AND POPULATION GROUP:")
    print("="*60)
    print(grouped_filtered.sort_values('incidents', ascending=False).head(20).to_string(index=False))
    print("\n💡 This heatmap highlights variations in incidents across geographic divisions and population groups!")

def plot_top_offenses(df: pd.DataFrame):
    """
    Plots a horizontal bar chart of the Top 15 most common offenses.
    
    """
    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    if 'offense' not in df.columns:
        print("Error: 'offense' column not found. Ensure DataFrame is unpivoted.")
        return

    # Count frequencies directly from the single 'offense' column
    # This automatically includes offenses from all slots (1-10)
    top_offenses = df['offense'].value_counts().head(15)
    
    # Calculate totals for percentage
    total_offenses_count = len(df)
    unique_offenses_count = df['offense'].nunique()

    # -------------------------------------------------------------------------
    # 2. Plotting
    # -------------------------------------------------------------------------
    plt.figure(figsize=(14, 8))
    
    # Create horizontal bars
    # Using a gradient orange color map
    colors = plt.cm.Oranges(np.linspace(0.9, 0.4, len(top_offenses)))
    bars = plt.barh(range(len(top_offenses)), top_offenses.values, color=colors)
    
    # Styling
    plt.yticks(range(len(top_offenses)), top_offenses.index, fontsize=11)
    plt.xlabel('Number of Offense Instances', fontsize=12, fontweight='bold')
    plt.title('Top 15 Most Common Offenses in US Hate Crimes', fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()  # Highest at top

    # Add value labels
    x_offset = top_offenses.max() * 0.01
    for i, v in enumerate(top_offenses.values):
        plt.text(v + x_offset, i, f'{v:,}', va='center', fontsize=10, fontweight='bold')

    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    # Show plot (if running in notebook) or just return figure if needed
    plt.show()

    # -------------------------------------------------------------------------
    # 3. Summary Output
    # -------------------------------------------------------------------------
    print("\n📊 TOP OFFENSES IN US HATE CRIMES:")
    print("="*60)
    
    for offense, count in top_offenses.items():
        pct = (count / total_offenses_count) * 100
        print(f"   {offense[:35]:35s}: {count:6,} ({pct:.1f}%)")

    print(f"\nTotal unique offense types: {unique_offenses_count}")
    print(f"Total offense instances analyzed: {total_offenses_count:,}")
    
    if not top_offenses.empty:
        print(f"\n💡 Most Common: '{top_offenses.index[0]}' accounts for "
              f"{(top_offenses.iloc[0]/total_offenses_count)*100:.1f}% of all reported offenses.")

def plot_offense_severity(df: pd.DataFrame):
    """
    Plots Offense Severity and Co-occurrence analysis.
    Adapts unpivoted data (long format) to analyze Primary vs Secondary offenses.
    
    1. Box Plot: Primary Offense vs Total Victims
    2. Heatmap: Likelihood of having a Secondary Offense given the Primary Offense
    """
    # -------------------------------------------------------------------------
    # 1. Data Preparation (Reconstructing Incident-Level Logic)
    # -------------------------------------------------------------------------
    if 'offense_index' not in df.columns:
        print("Error: 'offense_index' column missing. Cannot distinguish Primary/Secondary offenses.")
        return

    # A. Isolate Primary Offenses (Index 1) - This defines the "Incident Type"
    primary_df = df[df['offense_index'] == 1].copy()
    
    # B. Identify Incidents that HAVE a Secondary Offense (Index 2)
    # Get set of IDs that have a row with offense_index == 2
    ids_with_secondary = set(df[df['offense_index'] == 2]['incident_number'])
    ids_with_tertiary = set(df[df['offense_index'] == 3]['incident_number'])
    
    # Flag the primary dataframe
    primary_df['has_secondary'] = primary_df['incident_number'].isin(ids_with_secondary)
    primary_df['has_tertiary'] = primary_df['incident_number'].isin(ids_with_tertiary)

    # C. Determine Top 10 Primary Offenses for Visualization
    top_primary_offenses = primary_df['offense'].value_counts().head(10).index.tolist()
    
    # Filter data to only Top 10 for cleaner plotting
    plot_df = primary_df[primary_df['offense'].isin(top_primary_offenses)].copy()

    # -------------------------------------------------------------------------
    # 2. Plotting
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 1, figsize=(15, 15))
    
    # Define color palette
    # Create a simplified palette list for boxplot
    processed_palette = sns.color_palette("Oranges_r", n_colors=len(top_primary_offenses))

    # --- Plot 1: Box Plot (Victim Impact) ---
    # Order by frequency
    sns.boxplot(
        data=plot_df, 
        y='offense', 
        x='total_victims', 
        palette=processed_palette, 
        orient='h', 
        ax=axes[0], 
        order=top_primary_offenses
    )
    
    axes[0].set_title('Victim Impact by Primary Offense Type (Top 10)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Number of Victims per Incident', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Primary Offense', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)

    # --- Plot 2: Heatmap (Co-occurrence) ---
    # Calculate % of incidents for each primary offense that have a secondary offense
    co_occurrence = pd.crosstab(
        plot_df['offense'], 
        plot_df['has_secondary'], 
        normalize='index'
    ) * 100
    
    # Reindex to match the order of the box plot
    co_occurrence = co_occurrence.reindex(top_primary_offenses)
    
    co_occurrence.columns = ['Single Offense Only', 'Has Secondary Offense']

    sns.heatmap(
        co_occurrence[['Has Secondary Offense']], # Only show the "True" column
        annot=True, 
        fmt='.1f', 
        cmap='Oranges', 
        cbar_kws={'label': '% of Incidents with Secondary Offense'}, 
        ax=axes[1]
    )
    
    axes[1].set_title('Complexity Analysis: % of Incidents involving Multiple Offenses (Top 10)', 
                     fontsize=14, fontweight='bold')
    axes[1].set_xlabel('', fontsize=12) # Label is self-explanatory via column name
    axes[1].set_ylabel('Primary Offense', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 3. Summary Statistics
    # -------------------------------------------------------------------------
    print("\n📉 OFFENSE SEVERITY & IMPACT ANALYSIS (Top 10 Offenses):")
    print("="*60)
    
    total_incidents = len(primary_df)
    sec_count = primary_df['has_secondary'].sum()
    tert_count = primary_df['has_tertiary'].sum()
    
    print(f"\nTotal incidents analyzed: {len(plot_df):,} (Top 10 types cover {len(plot_df)/total_incidents*100:.1f}% of all data)")
    print(f"\nIncidents with secondary offenses: {sec_count:,} ({sec_count/total_incidents*100:.1f}%)")
    print(f"Incidents with tertiary offenses: {tert_count:,} ({tert_count/total_incidents*100:.1f}%)")

    print(f"\n📊 Average victims per incident (Top 10 Primary Offenses):")
    for offense in top_primary_offenses:
        subset = plot_df[plot_df['offense'] == offense]
        avg_victims = subset['total_victims'].mean()
        count = len(subset)
        print(f"   {offense[:35]:35s}: {avg_victims:.2f} avg victims ({count:,} incidents)")

    print("\n💡 INTERPRETATION:")
    print("   • Box plots show the range of victims (dots are outliers/mass casualty events).")
    print("   • Heatmap shows which crimes are 'complex' (likely to happen alongside other crimes).")

def plot_secondary_escalation(df: pd.DataFrame):
    """
    Analyzes and plots Secondary Offenses that occur in the same incident 
    as specific High-Rate Primary Offenses.
    
    Reconstructs the relationship between Primary (Index=1) and Secondary (Index>1)
    offenses using incident_number.
    """
    # -------------------------------------------------------------------------
    # 1. Data Preparation (Linking Primary to Secondary)
    # -------------------------------------------------------------------------

    if 'offense_index' not in df.columns:
        print("Error: 'offense_index' column missing.")
        return

    # Define the primary offenses to analyze
    high_secondary_primaries = [
        'Burglary/Breaking and Entering',
        'Other Larceny',
        'Drug/Narcotic Violations',
        'Aggravated Assault'
    ]

    # Step A: Get the rows for the TARGET Primary Offenses (Index 1)
    # We keep ID and Offense name to link later
    primary_subset = df[
        (df['offense_index'] == 1) & 
        (df['offense'].isin(high_secondary_primaries))
    ][['incident_number', 'offense']].rename(columns={'offense': 'Primary_Offense'})

    # Step B: Get the rows for ALL Secondary Offenses (Index > 1)
    secondary_subset = df[
        df['offense_index'] > 1
    ][['incident_number', 'offense']].rename(columns={'offense': 'Secondary_Offense'})

    # Step C: Merge to find pairs (Primary -> Secondary)
    # This creates a DataFrame where each row is a specific secondary offense 
    # linked to its primary trigger.
    merged_analysis = pd.merge(
        primary_subset, 
        secondary_subset, 
        on='incident_number', 
        how='inner' # Keep only incidents that HAVE a secondary offense
    )

    if merged_analysis.empty:
        print("No secondary offenses found for the selected primary offense types.")
        return

    # -------------------------------------------------------------------------
    # 2. Plotting
    # -------------------------------------------------------------------------
    plt.figure(figsize=(16, 12))
    
    # Create 2x2 subplots (since we have 4 primary types to analyze)
    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    axes = axes.flatten()

    for i, primary in enumerate(high_secondary_primaries):
        # Filter for this specific primary offense
        subset = merged_analysis[merged_analysis['Primary_Offense'] == primary]
        
        if not subset.empty:
            # Count top 5 secondary offenses
            top_secondary = subset['Secondary_Offense'].value_counts().head(5)
            total_secondary_count = len(subset)
            
            # Create horizontal bar chart
            colors = plt.cm.Oranges(np.linspace(0.9, 0.4, len(top_secondary)))
            axes[i].barh(range(len(top_secondary)), top_secondary.values, color=colors)
            
            axes[i].set_yticks(range(len(top_secondary)))
            axes[i].set_yticklabels(top_secondary.index, fontsize=10)
            axes[i].set_title(f'Secondary Offenses Following\n{primary}', fontsize=12, fontweight='bold')
            axes[i].set_xlabel('Number of Incidents')
            axes[i].invert_yaxis()
            axes[i].set_xlim(0, top_secondary.max() * 1.35) # Add space for labels

            # Add labels (Count + %)
            for j, (offense, count) in enumerate(top_secondary.items()):
                pct = (count / total_secondary_count) * 100
                axes[i].text(count + 1, j, f'{count} ({pct:.1f}%)', va='center', fontsize=9, fontweight='bold')
        else:
            axes[i].text(0.5, 0.5, 'No Secondary Offenses Found', ha='center', va='center')
            axes[i].set_title(f'{primary}', fontsize=12)

    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 3. Summary Statistics
    # -------------------------------------------------------------------------
    print("🔍 SECONDARY OFFENSE ANALYSIS (Escalation Patterns):")
    print("="*80)

    for primary in high_secondary_primaries:
        # Get counts from the original Primary Subset (Total Incidents)
        total_primary_incidents = len(primary_subset[primary_subset['Primary_Offense'] == primary])
        
        # Get counts from the Merged Analysis (Incidents with escalation)
        # Note: nunique() because one incident might have multiple secondary offenses (rows)
        escalated_incidents = merged_analysis[merged_analysis['Primary_Offense'] == primary]['incident_number'].nunique()
        
        # Specific secondary breakdown
        secondary_counts = merged_analysis[merged_analysis['Primary_Offense'] == primary]['Secondary_Offense'].value_counts().head(5)

        print(f"\n{primary.upper()}:")
        print(f"   Total incidents: {total_primary_incidents:,}")
        if total_primary_incidents > 0:
            print(f"   With secondary offenses: {escalated_incidents:,} ({escalated_incidents/total_primary_incidents*100:.1f}%)")
        
        if not secondary_counts.empty:
            print("   Top secondary offenses:")
            for offense, count in secondary_counts.items():
                # % here represents share of ALL secondary offenses for this primary type
                # For exact "what % of burglaries involve assault", we'd divide by total_primary_incidents
                pct_of_secondary = (count / len(merged_analysis[merged_analysis['Primary_Offense'] == primary])) * 100
                print(f"      {offense[:35]:35s}: {count:3d} ({pct_of_secondary:4.1f}% of secondary)")

    print("\n💡 ESCALATION INSIGHTS:")
    print("   • Property crimes (Burglary) often escalate to destruction/intimidation.")
    print("   • Drug violations frequently involve weapons or assault.")
    print("   • Understanding these pairs helps officer safety and prediction.")

def plot_top_bias_categories(df: pd.DataFrame):
    """
    Aggregates and plots the Top 10 Bias Categories across all offenses.
    Dynamically finds all columns ending in '_category' (e.g., bias_a_category).

    """
    print("🎯 TOP BIAS CATEGORY ANALYSIS:")
    print("="*50)

    # 1. Identify Bias Columns
    bias_cols = [col for col in df.columns if col.startswith('bias_') and col.endswith('_category')]
    
    if not bias_cols:
        print("No bias category columns found in the dataset.")
        return

    # 2. Efficiently Aggregate Data
    # Melt all bias columns into a single series and drop NaNs
    all_bias_series = df[bias_cols].melt()['value'].dropna()

    if all_bias_series.empty:
        print("No bias categories found in the data rows.")
        return

    # 3. Process Frequencies
    bias_counts = all_bias_series.value_counts()
    top_bias = bias_counts.head(10)
    
    total_bias_instances = bias_counts.sum()
    unique_categories = bias_counts.shape[0]

    # 4. Plotting
    plt.figure(figsize=(14, 8))
    colors = plt.cm.Oranges(np.linspace(0.9, 0.4, len(top_bias)))
    
    bars = plt.barh(range(len(top_bias)), top_bias.values, color=colors)
    plt.yticks(range(len(top_bias)), [cat[:40] for cat in top_bias.index], fontsize=11)
    plt.xlabel('Number of Offense Instances', fontsize=12, fontweight='bold')
    plt.title('Top 10 Bias Categories in US Hate Crimes', fontsize=16, fontweight='bold', pad=20)
    plt.xlim(0, top_bias.max() * 1.15)
    plt.gca().invert_yaxis()  # Highest at top

    # Add Value Labels
    for i, v in enumerate(top_bias.values):
        plt.text(v + (top_bias.max() * 0.01), i, f'{v:,}', va='center', fontsize=10, fontweight='bold')

    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 5. Summary Statistics
    print("\n📊 TOP BIAS CATEGORIES:")
    print("-" * 40)
    for category, count in top_bias.items():
        pct = (count / total_bias_instances) * 100
        print(f"   {category:35s}: {count:6,} ({pct:.1f}%)")

    print(f"\nTotal unique bias categories: {unique_categories}")
    print(f"Total bias instances analyzed: {total_bias_instances:,}")
    
    if not top_bias.empty:
        print(f"Most common: {top_bias.index[0]} ({top_bias.iloc[0]:,} instances)")

    print("\n💡 Race/Ethnicity bias usually dominates, highlighting the prevalence of racial motivations.")

def plot_top_bias_motivations(df: pd.DataFrame):
    """
    Aggregates and plots the Top 15 Specific Bias Motivations.
    Dynamically finds columns like bias_motivation_a, bias_motivation_b, etc.
    """
    print("🎯 TOP BIAS MOTIVATION ANALYSIS:")
    print("="*50)

    # 1. Identify Bias Motivation Columns (bias_motivation_a, etc.)
    # In unpivoted DF, looking for columns starting with 'bias_motivation_'
    bias_motivation_cols = [col for col in df.columns if col.startswith('bias_motivation_')]
    
    print(f"Available bias motivation columns: {len(bias_motivation_cols)}")

    if not bias_motivation_cols:
        print("No bias motivation columns found in the dataset.")
        return

    # 2. Aggregate Data
    all_bias_motivations = df[bias_motivation_cols].melt()['value'].dropna()

    if all_bias_motivations.empty:
        print("No bias motivations found in the data.")
        return

    # 3. Frequency Count
    motivation_counts = all_bias_motivations.value_counts()
    top_bias_motivations = motivation_counts.head(15)
    
    # 4. Visualization
    plt.figure(figsize=(14, 10))
    colors = plt.cm.Oranges(np.linspace(0.9, 0.4, len(top_bias_motivations)))
    
    plt.barh(range(len(top_bias_motivations)), top_bias_motivations.values, color=colors)
    plt.yticks(range(len(top_bias_motivations)), [mot[:40] for mot in top_bias_motivations.index], fontsize=11)
    plt.xlabel('Number of Incidents', fontsize=12, fontweight='bold')
    plt.title('Top 15 Specific Bias Motivations in US Hate Crimes', fontsize=16, fontweight='bold')
    plt.xlim(0, top_bias_motivations.max() * 1.1)
    plt.gca().invert_yaxis()  # Highest at top

    # Add Value Labels
    for i, v in enumerate(top_bias_motivations.values):
        plt.text(v + (top_bias_motivations.max() * 0.01), i, f'{v:,}', va='center', fontsize=10, fontweight='bold')

    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 5. Summary Statistics
    print("\n📊 TOP BIAS MOTIVATIONS:")
    print("-" * 45)
    total_motivation_instances = motivation_counts.sum()
    
    for motivation, count in top_bias_motivations.items():
        pct = (count / total_motivation_instances) * 100
        print(f"   {motivation:40s}: {count:6,} ({pct:.1f}%)")

    print(f"\nTotal unique bias motivations: {len(motivation_counts)}")
    print(f"Total motivation instances: {total_motivation_instances:,}")
    if not top_bias_motivations.empty:
        print(f"Most common: {top_bias_motivations.index[0]} ({top_bias_motivations.iloc[0]:,} instances)")
    
    print("\n💡 Anti-Black bias overwhelmingly dominates hate crimes, followed by anti-Jewish and anti-gay motivations!")

def plot_high_severity_motivations(df: pd.DataFrame):
    """
    Analyzes which Bias Motivations have the highest percentage of 
    'High Severity' incidents.
    
    Logic:
    1. Determine Max Severity per Unique Incident.
    2. Link all Motivations in that incident to the Incident's Max Severity.
    3. Calculate % of High Severity for top motivations.
    """
    print("🔥 BIAS MOTIVATIONS WITH HIGHEST SEVERITY:")
    print("="*60)

    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    if 'offense_severity' not in df.columns:
        print("Error: 'offense_severity' column missing.")
        return

    # A. Calculate Max Severity per Incident
    # Map severity to numeric for aggregation
    severity_rank = {'High': 3, 'Medium': 2, 'Low': 1, 'Non-Criminal': 0}
    df['severity_rank'] = df['offense_severity'].map(severity_rank).fillna(0)
    
    # Get the max severity rank per incident
    incident_max_severity = df.groupby('incident_number')['severity_rank'].max().reset_index()
    
    # Map numeric back to label (High/Medium/Low)
    rank_to_label = {3: 'High', 2: 'Medium', 1: 'Low', 0: 'Non-Criminal'}
    incident_max_severity['Max_Severity'] = incident_max_severity['severity_rank'].map(rank_to_label)

    # B. Get Unique Motivations per Incident
    # Identify bias motivation columns (bias_motivation_a, etc.)
    bias_cols = [col for col in df.columns if col.startswith('bias_motivation_')]
    
    if not bias_cols:
        print("No bias motivation columns found.")
        return

    # Melt to long format: One row per (Incident, Motivation)
    # We drop duplicates so we don't double count if an incident has 2 Anti-Black offenses
    incident_motivations = df[['incident_number'] + bias_cols].melt(
        id_vars='incident_number', 
        value_name='Motivation'
    ).dropna()
    
    # Get unique motivations per incident
    incident_motivations = incident_motivations[['incident_number', 'Motivation']].drop_duplicates()

    # C. Merge Severity with Motivations
    merged_df = pd.merge(incident_motivations, incident_max_severity, on='incident_number', how='inner')

    # -------------------------------------------------------------------------
    # 2. Aggregation & Calculation
    # -------------------------------------------------------------------------
    # Filter to only the most common motivations (Top 15) to ensure statistical significance
    top_motivations_list = merged_df['Motivation'].value_counts().head(15).index.tolist()
    
    severity_comparison = []

    for motivation in top_motivations_list:
        subset = merged_df[merged_df['Motivation'] == motivation]
        total_incidents = len(subset)
        high_sev_count = len(subset[subset['Max_Severity'] == 'High'])
        
        pct_high = (high_sev_count / total_incidents) * 100 if total_incidents > 0 else 0
        
        severity_comparison.append({
            'Motivation': motivation,
            'High_Severity_Pct': pct_high,
            'Total_Incidents': total_incidents
        })

    # Create Analysis DataFrame and sort by Severity %
    severity_df = pd.DataFrame(severity_comparison).sort_values('High_Severity_Pct', ascending=True)

    # -------------------------------------------------------------------------
    # 3. Visualization
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Gradient bars based on severity %
    colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(severity_df)))
    bars = ax.barh(range(len(severity_df)), severity_df['High_Severity_Pct'], color=colors)
    
    ax.set_yticks(range(len(severity_df)))
    ax.set_yticklabels([m[:30] for m in severity_df['Motivation']], fontsize=11)
    ax.set_xlabel('Percentage of Incidents classified as "High Severity" (%)', fontsize=12, fontweight='bold')
    ax.set_title('Which Hate Motivations are Most Violent?\n(High Severity Rate among Top 15 Motivations)', 
                fontsize=15, fontweight='bold', pad=20)
    
    ax.set_xlim(0, severity_df['High_Severity_Pct'].max() * 1.15)

    # Add Percentage Labels
    for i, pct in enumerate(severity_df['High_Severity_Pct']):
        ax.text(pct + 0.5, i, f'{pct:.1f}%', va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 4. Summary Output
    # -------------------------------------------------------------------------
    print("\n📊 HIGH-SEVERITY BIAS MOTIVATIONS ANALYSIS:")
    print("-" * 50)
    
    # --- ADDED: Absolute counts of high-severity offenses ---
    high_sev_motivations = merged_df[merged_df['Max_Severity'] == 'High']
    total_high_sev_incidents = len(high_sev_motivations)
    top_high_sev_counts = high_sev_motivations['Motivation'].value_counts().head(10)

    print(f"Total incidents with high-severity offenses: {total_high_sev_incidents:,}")

    print(f"\n🔴 TOP MOTIVATIONS WITH HIGH-SEVERITY OFFENSES:")
    for motivation, count in top_high_sev_counts.items():
        pct = (count / total_high_sev_incidents) * 100
        print(f"   {motivation:35s}: {count:4d} ({pct:.1f}%)")

    # --- EXISTING: Rate of high-severity per motivation ---
    print(f"\n📈 HIGH-SEVERITY RATES FOR TOP MOTIVATIONS:")
    # Sort descending for print output
    print_df = severity_df.sort_values('High_Severity_Pct', ascending=False)
    
    for _, row in print_df.iterrows():
        print(f"   {row['Motivation']:35s}: {row['High_Severity_Pct']:5.1f}% high-severity "
              f"({row['Total_Incidents']:,} total incidents)")

    print(f"\n💡 KEY INSIGHT: High severity flags crimes involving death or serious injury.")
    print(f"   Motivations at the top of this chart tend to result in more violent outcomes.")

def plot_critical_bias_trends(df: pd.DataFrame):
    """
    Analyzes Year-over-Year trends for specific 'Critical' Bias Motivations.
    
    Methodology:
    - Aggregates by UNIQUE INCIDENT (to avoid overcounting multi-offense incidents).
    - Checks all bias columns (a, b, c, etc.) to capture the motivation regardless of position.
    """
    print("📈 YEAR-OVER-YEAR TRENDS FOR CRITICAL BIAS MOTIVATIONS:")
    print("="*70)

    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    if 'year' not in df.columns:
        print("Error: 'year' column missing.")
        return

    # Define Critical Motivations
    critical_motivations = [
        'Anti-Black or African American',  # Highest absolute numbers
        'Anti-Jewish',                     # Second highest absolute numbers
        'Anti-Gay (Male)',                 # High severity rate
        'Anti-Hispanic or Latino',         # High severity rate
        'Anti-Asian'                       # Emerging threat
    ]

    print(f"Analyzing trends for {len(critical_motivations)} critical bias motivations:")
    for i, mot in enumerate(critical_motivations, 1):
        print(f"  {i}. {mot}")
    print()

    # Identify all bias motivation columns available (bias_motivation_a, etc.)
    bias_cols = [col for col in df.columns if col.startswith('bias_motivation_')]

    # Melt data to get one row per (Incident, Year, Motivation)
    # This captures the bias regardless of which column (a, b, c) it appears in
    long_bias = df.melt(
        id_vars=['incident_number', 'year'], 
        value_vars=bias_cols, 
        value_name='Motivation'
    ).dropna()

    # Filter for only the critical motivations we care about
    long_bias = long_bias[long_bias['Motivation'].isin(critical_motivations)]

    # Count UNIQUE Incidents per Year per Motivation
    # unstack(fill_value=0) ensures we have 0s for years with no incidents instead of NaNs
    yearly_trends = long_bias.groupby(['year', 'Motivation'])['incident_number'].nunique().unstack(fill_value=0)

    # Reindex to ensure all critical motivations are columns (even if 0 counts)
    for mot in critical_motivations:
        if mot not in yearly_trends.columns:
            yearly_trends[mot] = 0
            
    # Ensure columns are in the specific order of our list
    yearly_trends = yearly_trends[critical_motivations]

    # Calculate Growth Rates
    growth_rates = yearly_trends.pct_change() * 100

    # -------------------------------------------------------------------------
    # 2. Visualization
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))
    fig.suptitle('Year-over-Year Trends: Critical Bias Motivations', fontsize=16, fontweight='bold')

    # Color scheme
    colors = plt.cm.Oranges(np.linspace(0.8, 0.2, len(critical_motivations)))

    # --- Plot 1: Absolute Incident Counts ---
    x = np.arange(len(yearly_trends.index))
    width = 0.15

    for i, motivation in enumerate(critical_motivations):
        offset = width * (i - 2)
        bars = axes[0].bar(x + offset, yearly_trends[motivation], width, 
                           label=motivation[:25], color=colors[i])
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                axes[0].text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=11, fontweight='bold')

    axes[0].set_title('Absolute Incident Counts by Year (Unique Incidents)', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Number of Incidents')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(yearly_trends.index)
    axes[0].legend(bbox_to_anchor=(1.01, 1), loc='upper left')
    axes[0].grid(True, alpha=0.3, axis='y')

    # --- Plot 2: Growth Rates ---
    for i, motivation in enumerate(critical_motivations):
        offset = width * (i - 2)
        # Skip first year (NaN growth)
        valid_years = growth_rates.index[1:]
        valid_values = growth_rates[motivation].iloc[1:].values
        
        bars = axes[1].bar(x[1:] + offset, valid_values, width,
                           label=motivation[:25], color=colors[i])
        
        # Add labels
        for bar, val in zip(bars, valid_values):
            if not np.isnan(val) and abs(val) > 1:
                height = bar.get_height()
                label_y = height if height > 0 else 0
                axes[1].text(bar.get_x() + bar.get_width()/2., label_y,
                           f'{val:.1f}%',
                           ha='center', va='bottom' if height > 0 else 'top',
                           fontsize=10, fontweight='bold')

    axes[1].axhline(y=0, color='black', linestyle='--', alpha=0.5, linewidth=1)
    axes[1].set_title('Year-over-Year Growth Rates (%)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Year')
    axes[1].set_ylabel('Growth Rate (%)')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(yearly_trends.index)
    axes[1].legend(bbox_to_anchor=(1.01, 1), loc='upper left')
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 3. Emerging Threats Analysis
    # -------------------------------------------------------------------------
    print("\n🚨 EMERGING THREATS ANALYSIS:")
    print("-" * 40)

    # Calculate average growth rates for available years (excluding the base year)
    if len(growth_rates) > 1:
        avg_growth_rates = growth_rates.iloc[1:].mean()

        print("Average Year-over-Year Growth Rates:")
        for motivation in critical_motivations:
            avg = avg_growth_rates.get(motivation, 0)
            print(f"  {motivation:30s}: {avg:6.1f}%")

        # Insight Logic
        print(f"\n📊 TREND INSIGHTS:")
        print(f"   • Anti-Black incidents: Most numerous but showing {'increasing' if avg_growth_rates.get('Anti-Black or African American', 0) > 0 else 'declining'} trend")
        print(f"   • Anti-Jewish incidents: {'Rapid growth' if avg_growth_rates.get('Anti-Jewish', 0) > 20 else 'Moderate growth'} - potential emerging threat")
        print(f"   • Anti-Gay incidents: {'Increasing' if avg_growth_rates.get('Anti-Gay (Male)', 0) > 10 else 'Stable'} trend")
        print(f"   • Anti-Hispanic incidents: {'Strong growth' if avg_growth_rates.get('Anti-Hispanic or Latino', 0) > 15 else 'Stable'} trend")
        print(f"   • Anti-Asian incidents: {'Growing' if avg_growth_rates.get('Anti-Asian', 0) > 0 else 'Declining'} trend")

        # Identify fastest growing
        if not avg_growth_rates.empty:
            fastest = avg_growth_rates.idxmax()
            fastest_rate = avg_growth_rates.max()
            print(f"\n⚠️  FASTEST GROWING THREAT: {fastest} ({fastest_rate:.1f}% avg growth)")
            print(f"   This represents an emerging threat that requires increased attention!")
    
    print(f"\n💡 Emerging threats are motivations showing rapid growth even if absolute numbers")
    print(f"   are still lower than traditional categories like Anti-Black bias.")

def plot_bias_cooccurrence(df: pd.DataFrame):
    """
    Analyzes the co-occurrence of Bias Categories within UNIQUE incidents.
    
    Logic:
    1. Aggregates all bias categories (a, b, c...) from ALL offenses within an incident.
    2. Identifies incidents that have >1 distinct bias category.
    3. Counts pairs and plots a heatmap.
    """
    print("🔗 BIAS CATEGORY CO-OCCURRENCE ANALYSIS:")
    print("="*60)

    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    # Identify bias category columns (e.g., bias_a_category)
    bias_cols = [col for col in df.columns if col.startswith('bias_') and col.endswith('_category')]
    print(f"Found {len(bias_cols)} bias category columns scanning for co-occurrences.")

    if not bias_cols:
        return

    # Step A: Melt to get (Incident, Bias) pairs
    # This collects every bias mentioned in every offense of the incident
    long_biases = df.melt(
        id_vars=['incident_number'],
        value_vars=bias_cols,
        value_name='Bias_Category'
    ).dropna()

    # Step B: Consolidate to Unique Biases per Incident
    # grouping by incident and getting unique values ensures we don't count the same bias 
    # twice for the same incident (e.g. two Anti-Black offenses = 1 Anti-Black bias for the incident)
    incident_biases = long_biases.groupby('incident_number')['Bias_Category'].unique()

    # Step C: Filter for Multi-Bias Incidents
    # We only care about incidents with 2 or more DIFFERENT categories
    multi_bias_incidents = incident_biases[incident_biases.apply(len) > 1]
    
    total_incidents = df['incident_number'].nunique()
    total_multi = len(multi_bias_incidents)
    
    print(f"Incidents with multiple distinct bias categories: {total_multi:,} ({total_multi/total_incidents*100:.1f}%)")

    if total_multi == 0:
        print("No incidents found with multiple bias categories.")
        return

    # -------------------------------------------------------------------------
    # 2. Pair Counting
    # -------------------------------------------------------------------------
    pair_counts = Counter()

    for biases in multi_bias_incidents:
        # Sort to ensure (Race, Religion) is treated same as (Religion, Race)
        for pair in combinations(sorted(biases), 2):
            pair_counts[pair] += 1

    # Get Top 10 Pairs
    top_pairs = pair_counts.most_common(10)
    
    # Create Table Data
    top_pairs_data = []
    for rank, (pair, count) in enumerate(top_pairs, 1):
        top_pairs_data.append({
            'Rank': rank,
            'Bias 1': pair[0],
            'Bias 2': pair[1],
            'Count': count,
            'Pct': (count / total_multi) * 100
        })
    
    top_pairs_df = pd.DataFrame(top_pairs_data)

    print("\n📊 TOP 10 BIAS CATEGORY CO-OCCURRENCE PAIRS:")
    print("="*80)
    print(top_pairs_df.to_string(index=False, float_format='%.1f'))

    # -------------------------------------------------------------------------
    # 3. Visualization (Heatmap)
    # -------------------------------------------------------------------------
    # Gather all unique categories involved in the top pairs for the matrix
    categories_in_pairs = set()
    for pair, _ in top_pairs:
        categories_in_pairs.update(pair)
    
    sorted_cats = sorted(list(categories_in_pairs))
    
    # Init empty matrix
    matrix = pd.DataFrame(0, index=sorted_cats, columns=sorted_cats)
    
    # Fill matrix
    for (b1, b2), count in top_pairs:
        matrix.loc[b1, b2] = count
        matrix.loc[b2, b1] = count # Symmetric

    plt.figure(figsize=(12, 10))
    sns.heatmap(matrix, annot=True, fmt='d', cmap='Oranges',
                cbar_kws={'label': 'Co-occurrence Count'}, square=True)
    
    plt.title('Top 10 Bias Category Co-occurrence Pairs', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 4. Insights
    # -------------------------------------------------------------------------
    print(f"\n💡 INSIGHTS:")
    print(f"   • Total unique incidents: {total_incidents:,}")
    if top_pairs:
        top_pair_str = f"{top_pairs[0][0][0]} + {top_pairs[0][0][1]}"
        print(f"   • Most common co-occurrence: {top_pair_str} ({top_pairs[0][1]} incidents)")
        print(f"   • This pair accounts for {top_pairs[0][1]/total_multi*100:.1f}% of all complex bias incidents.")

    # Frequency analysis
    bias_in_pairs = Counter()
    for pair, count in top_pairs:
        for b in pair:
            bias_in_pairs[b] += count

    print(f"\n🎯 CATEGORIES MOST FREQUENTLY INVOLVED IN CO-OCCURRENCES:")
    for bias, count in bias_in_pairs.most_common(5):
        print(f"   • {bias}: appears in {count} top-pair instances")

def plot_bias_motivations_by_region(df: pd.DataFrame):
    """
    Analyzes and plots the Regional Distribution of Top 8 Bias Motivations.
    
    Logic:
    1. Melts all bias columns (a, b, c...) to long format.
    2. Aggregates unique incidents per Region + Motivation.
    3. Normalizes to show the % composition of hate crime types in each region.
    """
    print("🗺️ BIAS MOTIVATIONS BY REGION ANALYSIS:")
    print("="*60)

    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    if 'country_region' not in df.columns:
        print("Error: 'country_region' column missing.")
        return

    # Filter out missing regions
    df_region = df.dropna(subset=['country_region']).copy()
    
    # Identify bias motivation columns (bias_motivation_a, etc.)
    bias_cols = [col for col in df.columns if col.startswith('bias_motivation_')]
    print(f"Found {len(bias_cols)} bias motivation columns.")

    if not bias_cols:
        return

    # Melt to long format: (Unique Incident, Region, Motivation)
    long_bias = df_region.melt(
        id_vars=['incident_number', 'country_region'],
        value_vars=bias_cols,
        value_name='Bias Motivation'
    ).dropna()

    # Deduplicate: Ensure we count a specific bias only once per incident per region
    # (e.g. if an incident has 2 'Anti-Black' offenses, count it as 1 Anti-Black incident)
    long_bias = long_bias[['incident_number', 'country_region', 'Bias Motivation']].drop_duplicates()

    # Count Incidents per Region per Motivation
    region_counts = long_bias.groupby(['country_region', 'Bias Motivation']).size().reset_index(name='Count')

    # -------------------------------------------------------------------------
    # 2. Filter Top Motivations
    # -------------------------------------------------------------------------
    # Get top 8 bias motivations globally
    top_8_motivations = region_counts.groupby('Bias Motivation')['Count'].sum().nlargest(8).index.tolist()
    
    # Filter dataset to just these top 8
    top_region_df = region_counts[region_counts['Bias Motivation'].isin(top_8_motivations)].copy()

    # Pivot: Index=Motivation, Columns=Region, Values=Count
    pivot_df = top_region_df.pivot_table(
        values='Count',
        index='Bias Motivation',
        columns='country_region',
        fill_value=0
    )

    # Sort motivations by global total (for consistent chart ordering)
    motivation_totals = pivot_df.sum(axis=1).sort_values(ascending=False)
    pivot_df = pivot_df.loc[motivation_totals.index]

    print("\n📊 TOP 8 BIAS MOTIVATIONS BY REGION (Incident Counts):")
    print("="*80)
    print(pivot_df.to_string(float_format='%.0f'))

    # -------------------------------------------------------------------------
    # 3. Visualization (Stacked Bar Chart)
    # -------------------------------------------------------------------------
    # Calculate percentages: What % of a Region's incidents are Motivation X?
    # Axis=0 sums down the column (Total Region Incidents)
    region_totals = pivot_df.sum(axis=0)
    pivot_pct = pivot_df.div(region_totals, axis=1) * 100

    plt.figure(figsize=(14, 8))
    
    # Transpose for plotting: X-axis = Region, Stack = Motivation
    ax = pivot_pct.T.plot(
        kind='bar', 
        stacked=True, 
        figsize=(14, 8),
        colormap='Oranges_r', 
        width=0.8
    )

    plt.title('Regional Distribution of Top 8 Bias Motivations (%)', fontsize=16, fontweight='bold')
    plt.xlabel('Region', fontsize=12, fontweight='bold')
    plt.ylabel('Percentage of Regional Incidents', fontsize=12, fontweight='bold')
    plt.legend(title='Bias Motivation', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 4. Regional Insights
    # -------------------------------------------------------------------------
    print("\n🏛️ REGIONAL INSIGHTS:")
    print("="*50)

    regions = pivot_df.columns.tolist()
    
    for region in regions:
        region_total = pivot_df[region].sum()
        if region_total > 0:
            top_motivation = pivot_df[region].idxmax()
            top_count = pivot_df[region].max()
            top_pct = (top_count / region_total) * 100

            print(f"\n{region.upper()}:")
            print(f"   • Total analyzed incidents: {region_total:,.0f}")
            print(f"   • Top bias motivation: {top_motivation}")
            print(f"   • Dominance: {top_pct:.1f}% of regional incidents")

    # Concentration Analysis
    # Range = Max % across regions - Min % across regions
    concentration_df = pivot_pct.max(axis=1) - pivot_pct.min(axis=1)
    most_concentrated = concentration_df.idxmax()
    least_concentrated = concentration_df.idxmin()

    print(f"\n🌍 DISTRIBUTION PATTERNS:")
    print(f"   • Largest region by incidents: {pivot_df.sum(axis=0).idxmax()} ({pivot_df.sum(axis=0).max():,.0f} incidents)")
    print(f"   • Smallest region by incidents: {pivot_df.sum(axis=0).idxmin()} ({pivot_df.sum(axis=0).min():,.0f} incidents)")

    print(f"   • Most regionally concentrated: {most_concentrated} (Varies by {concentration_df.max():.1f}% across regions)")
    print(f"   • Most evenly distributed: {least_concentrated} (Varies by only {concentration_df.min():.1f}%)")

    # Unique Dominance Check
    dominant_biases = {r: pivot_df[r].idxmax() for r in regions if pivot_df[r].sum() > 0}
    unique_dominants = set(dominant_biases.values())

    # Possessions has too few incidents -> "ignorable" if all other regions share the same dominant bias
    dominant_excluding_possessions = {r: bias for r, bias in dominant_biases.items() if r != "Possessions"}
    unique_excluding_possessions = set(dominant_excluding_possessions.values())

    # All regions including possessions match
    if len(unique_dominants) == 1:
        print(f"   • Regional Uniformity: All regions share the same dominant motivation: {list(unique_dominants)[0]}.")
    # All regions except possessions match
    elif len(unique_excluding_possessions) == 1:
        print(f"   • Regional Near-Uniformity: All major US regions share the same dominant motivation "
          f"(excluding Possessions): {list(unique_excluding_possessions)[0]}. ")
    # True diversity
    else:
        print(f"   • Regional Diversity: Distinct bias patterns found ({len(unique_dominants)} different dominant motivations).")

def plot_top_locations(df: pd.DataFrame):
    """
    Analyzes and plots the Top Locations where Hate Crimes occur.
    
    Methodology:
    - Counts UNIQUE INCIDENTS per location.
    - If an incident has multiple offenses at the same location, it counts as 1.
    """
    print("🏠 TOP LOCATIONS FOR HATE CRIMES ANALYSIS:")
    print("="*50)

    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    if 'location' not in df.columns:
        print("Error: 'location' column missing.")
        return

    # Deduplicate: Get unique (Incident, Location) pairs
    # This prevents counting "Residence" 3 times if one incident has 3 offenses at home.
    unique_locations_df = df[['incident_number', 'location']].dropna().drop_duplicates()
    
    total_location_instances = len(unique_locations_df)
    
    # Count frequencies
    location_counts = unique_locations_df['location'].value_counts()
    
    # Top 15 Locations
    top_locations = location_counts.head(15)
    
    # -------------------------------------------------------------------------
    # 2. Visualization 1: Horizontal Bar Chart (Top 15)
    # -------------------------------------------------------------------------
    print("\n📊 TOP 15 LOCATIONS FOR HATE CRIMES:")
    print("="*60)
    print(f"{'Rank':<4} {'Location':<35} {'Count':<8} {'Percentage'}")
    print("-" * 60)
    
    for i, (location, count) in enumerate(top_locations.items(), 1):
        pct = (count / total_location_instances) * 100
        print(f"{i:<4} {location[:35]:<35} {count:<8,} {pct:.1f}%")

    plt.figure(figsize=(14, 10))
    colors = plt.cm.Oranges(np.linspace(0.9, 0.4, len(top_locations)))
    
    plt.barh(range(len(top_locations)), top_locations.values, color=colors)
    plt.yticks(range(len(top_locations)), 
               [loc[:30] + '...' if len(loc) > 30 else loc for loc in top_locations.index], 
               fontsize=11)
    
    plt.xlabel('Number of Unique Incidents', fontsize=12, fontweight='bold')
    plt.ylabel('Location', fontsize=12, fontweight='bold')
    plt.title('Top 15 Locations for Hate Crimes', fontsize=16, fontweight='bold', pad=20)
    plt.gca().invert_yaxis()  # Highest at top

    # Add value labels
    for i, v in enumerate(top_locations.values):
        pct = (v / total_location_instances) * 100
        plt.text(v + (top_locations.max() * 0.01), i, f'{v:,} ({pct:.1f}%)', va='center', fontsize=9, fontweight='bold')

    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 3. Visualization 2: Pie Chart (Top 8 + Other)
    # -------------------------------------------------------------------------
    plt.figure(figsize=(12, 10))
    
    top_8 = location_counts.head(8)
    other_count = total_location_instances - top_8.sum()
    
    pie_labels = top_8.index.tolist()
    pie_counts = top_8.values.tolist()
    
    if other_count > 0:
        pie_labels.append('Other Locations')
        pie_counts.append(other_count)
        
    pie_colors = plt.cm.Oranges(np.linspace(0, 0.8, len(pie_labels))) # Darker oranges
    
    plt.pie(pie_counts, labels=pie_labels, autopct='%1.1f%%', startangle=90, 
            colors=pie_colors, pctdistance=0.85, textprops={'fontsize': 10})
            
    plt.title('Distribution of Hate Crime Locations (Top 8 + Other)', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 4. Location Category Analysis
    # -------------------------------------------------------------------------
    print("\n🏷️ LOCATION CATEGORY ANALYSIS:")
    print("="*40)

    # Define Categories
    categories_map = {
        'Residential': ['Residence/Home'],
        'Transportation': ['Highway/Road/Alley', 'Air/Bus/Train Terminal', 'Parking Lot/Garage'],
        'Educational': ['School - Elementary/Secondary', 'School - College/University'],
        'Religious': ['Church/Synagogue/Temple'],
        'Commercial': ['Restaurant', 'Bar/Nightclub', 'Convenience Store', 'Commercial/Office Building', 
                       "Drug Store/Dr.'s Office/Hospital", 'Bank/Savings and Loan', 'Grocery/Supermarket', 'Shopping Mall'],
        'Public/Recreational': ['Park/Playground', 'Government/Public Building'],
        'Other/Unknown': ['Other/Unknown']
    }

    # Aggregate counts by category using the 'location_counts' series derived from unique incidents
    cat_counts = {}
    for cat, locs in categories_map.items():
        total = 0
        for loc in locs:
            total += location_counts.get(loc, 0)
        cat_counts[cat] = total
        
    # Sort
    sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)

    for cat, total in sorted_cats:
        pct = (total / total_location_instances) * 100
        print(f"   • {cat:20s}: {total:6,} ({pct:5.1f}%)")

    # Category Bar Chart
    plt.figure(figsize=(12, 8))
    cat_names = [x[0] for x in sorted_cats]
    cat_vals = [x[1] for x in sorted_cats]
    
    plt.bar(cat_names, cat_vals, color=plt.cm.Oranges(np.linspace(0.8, 0.3, len(cat_names))))
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Number of Unique Incidents', fontsize=12, fontweight='bold')
    plt.title('Hate Crime Incidents by Location Category', fontsize=16, fontweight='bold')
    
    for i, v in enumerate(cat_vals):
        plt.text(i, v + (max(cat_vals)*0.01), f'{v:,}', ha='center', va='bottom', fontsize=10)

    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 5. Prevention Implications
    # -------------------------------------------------------------------------
    print("\n🎯 PREVENTION IMPLICATIONS:")
    print("="*30)
    
    top_loc = top_locations.index[0]
    top_cat = sorted_cats[0][0]
    
    print(f"   • Primary Focus: {top_cat} areas (specifically '{top_loc}'), which account for the majority of incidents.")
    print("   • Public Spaces: Monitor transportation hubs and parking areas.")
    print("   • Institutions: Enhance security at schools and places of worship.")
    print("   • Commercial: Community education in high-risk retail/commercial areas.")

def plot_bias_location_heatmap(df: pd.DataFrame):
    """
    Analyzes the relationship between Bias Categories and Locations.
    
    Methodology:
    1. Collects all Bias Categories associated with a Unique Incident (across all offense rows).
    2. Collects all Locations associated with a Unique Incident.
    3. Creates (Bias, Location) pairs for the incident.
    4. Aggregates to find where specific biases tend to occur.
    """
    print("📍 TOP BIAS CATEGORIES BY LOCATION ANALYSIS:")
    print("="*60)

    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    if 'location' not in df.columns:
        print("Error: 'location' column missing.")
        return

    # Identify bias category columns (e.g., bias_a_category)
    bias_cols = [col for col in df.columns if col.startswith('bias_') and col.endswith('_category')]
    print(f"Found {len(bias_cols)} bias category columns.")

    if not bias_cols:
        return

    # Step A: Melt Bias Categories to long format
    # Result: Rows of (incident_number, location, Bias_Category)
    # Note: We include 'location' in id_vars to keep the link between the specific offense row's location and its bias
    # However, since we care about the INCIDENT level, we will aggregate shortly.
    long_data = df.melt(
        id_vars=['incident_number', 'location'],
        value_vars=bias_cols,
        value_name='Bias_Category'
    ).dropna(subset=['Bias_Category', 'location'])

    # Step B: Deduplicate at Incident Level
    # If an incident has 3 offenses, all "Anti-Black" at "Residence", we count it as ONE instance of (Anti-Black, Residence)
    incident_pairs = long_data[['incident_number', 'Bias_Category', 'location']].drop_duplicates()

    # -------------------------------------------------------------------------
    # 2. Filtering & Crosstab
    # -------------------------------------------------------------------------
    # Get Top 8 Bias Categories (by total incident count)
    top_biases = incident_pairs['Bias_Category'].value_counts().head(8).index.tolist()
    
    # Get Top 15 Locations (by total incident count)
    top_locations = incident_pairs['location'].value_counts().head(15).index.tolist()

    # Filter data
    filtered_pairs = incident_pairs[
        (incident_pairs['Bias_Category'].isin(top_biases)) & 
        (incident_pairs['location'].isin(top_locations))
    ]

    # Create Crosstab: Rows = Bias, Cols = Location
    crosstab = pd.crosstab(filtered_pairs['Bias_Category'], filtered_pairs['location'])
    
    # Sort Rows (Biases) by total volume
    crosstab = crosstab.loc[crosstab.sum(axis=1).sort_values(ascending=False).index]
    # Sort Columns (Locations) by total volume
    crosstab = crosstab[crosstab.sum(axis=0).sort_values(ascending=False).index]

    print("\n📊 TOP BIAS CATEGORIES BY LOCATION (Top 15 Locations):")
    print("="*90)
    print(crosstab.to_string(float_format='%.0f'))

    # -------------------------------------------------------------------------
    # 3. Visualization 1: Heatmap
    # -------------------------------------------------------------------------
    plt.figure(figsize=(16, 10))
    sns.heatmap(crosstab, annot=True, fmt='d', cmap='Oranges',
                cbar_kws={'label': 'Number of Unique Incidents'}, square=False)
    
    plt.title('Top Bias Categories by Location (Top 15 Locations)', fontsize=16, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 4. Visualization 2: Stacked Bar (Top 5 Locations per Bias)
    # -------------------------------------------------------------------------
    # Calculate % distribution for each bias
    # (e.g., For Anti-Jewish crimes, X% happen at Home, Y% at Church)
    
    # We need the full location breakdown for these top biases, not just the top 15 locations
    full_crosstab = pd.crosstab(
        incident_pairs[incident_pairs['Bias_Category'].isin(top_biases)]['Bias_Category'], 
        incident_pairs[incident_pairs['Bias_Category'].isin(top_biases)]['location']
    )
    
    # Convert to percentage rows
    row_pcts = full_crosstab.div(full_crosstab.sum(axis=1), axis=0) * 100
    
    # Extract top 5 locations for each bias for the stacked chart
    top_5_data = {}
    all_top_locs = set()
    
    for bias in top_biases:
        if bias in row_pcts.index:
            top_5 = row_pcts.loc[bias].nlargest(5)
            top_5_data[bias] = top_5
            all_top_locs.update(top_5.index)
            
    # Reconstruct a DataFrame for plotting only these specific (Bias, Location) combos
    plot_df = pd.DataFrame(0.0, index=top_biases, columns=sorted(list(all_top_locs)))
    for bias, series in top_5_data.items():
        for loc, val in series.items():
            plot_df.loc[bias, loc] = val

    plt.figure(figsize=(16, 10))
    ax = plot_df.plot(kind='barh', stacked=True, figsize=(16, 10),
                       color=plt.cm.Oranges(np.linspace(0.9, 0.4, len(all_top_locs))), width=0.8)

    plt.title('Top 5 Locations for Each Bias Category (%)', fontsize=16, fontweight='bold')
    plt.xlabel('Percentage of Incidents', fontsize=12, fontweight='bold')
    plt.ylabel('Bias Category', fontsize=12, fontweight='bold')
    plt.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 5. Detailed Insights
    # -------------------------------------------------------------------------
    print("\n🏛️ BIAS CATEGORY LOCATION INSIGHTS:")
    print("="*50)

    for bias in top_biases:
        if bias in full_crosstab.index:
            total_incidents = full_crosstab.loc[bias].sum()
            top_loc = full_crosstab.loc[bias].idxmax()
            top_count = full_crosstab.loc[bias].max()
            top_pct = (top_count / total_incidents) * 100

            print(f"\n{bias.upper()}:")
            print(f"   • Total incidents: {total_incidents:,.0f}")
            print(f"   • Most common location: {top_loc}")
            print(f"   • Location dominance: {top_count:,.0f} incidents ({top_pct:.1f}%)")

            # Show top 3
            top_3 = full_crosstab.loc[bias].nlargest(3)
            print("   • Top 3 locations:")
            for i, (loc, count) in enumerate(top_3.items(), 1):
                pct = (count / total_incidents) * 100
                print(f"      {i}. {loc}: {count:,.0f} ({pct:.1f}%)")

    # Overall Patterns
    print(f"\n🌍 OVERALL LOCATION PATTERNS:")
    total_obs = full_crosstab.sum().sum()
    overall_top_loc = full_crosstab.sum(axis=0).idxmax()
    overall_top_count = full_crosstab.sum(axis=0).max()
    overall_top_pct = overall_top_count / total_obs * 100
    
    print(f"   • Most common location overall: {overall_top_loc}")
    print(f"   • Total incidents at this location: {overall_top_count:,.0f} ({overall_top_pct:.1f}%)")
    
    print(f"\n💡 This analysis reveals where different types of hate crimes are most likely to occur!")
    print(f"   Understanding location patterns can help with prevention and response strategies.")

def plot_location_severity_risk(df: pd.DataFrame):
    """
    Analyzes the Severity Distribution (High/Medium/Low) for Top 10 Locations.
    
    Methodology:
    1. Determines the 'Highest Severity' for each Unique Incident across all its offenses.
    2. Identifies Top 10 Locations by incident volume.
    3. Calculates the % mix of severity for incidents occurring at those locations.
    """
    print("🏠 LOCATION RISK ASSESSMENT: SEVERITY DISTRIBUTION")
    print("="*60)

    # -------------------------------------------------------------------------
    # 1. Data Preparation
    # -------------------------------------------------------------------------
    if 'offense_severity' not in df.columns:
        print("Error: 'offense_severity' column missing.")
        return
        
    if 'location' not in df.columns:
        print("Error: 'location' column missing.")
        return

    # A. Calculate Highest Severity per Incident
    # Define hierarchy
    severity_map = {'High': 3, 'Medium': 2, 'Low': 1, 'Non-Criminal': 0}
    reverse_map = {3: 'High', 2: 'Medium', 1: 'Low', 0: 'Non-Criminal'}
    
    # Map to rank
    df['severity_rank'] = df['offense_severity'].map(severity_map).fillna(0)
    
    # Group by Incident to get Max Rank
    incident_max_severity = df.groupby('incident_number')['severity_rank'].max().reset_index()
    incident_max_severity['Highest_Severity'] = incident_max_severity['severity_rank'].map(reverse_map)

    # Display overall distribution
    print(f"Severity distribution across all incidents:")
    sev_counts = incident_max_severity['Highest_Severity'].value_counts()
    total_incidents = len(incident_max_severity)
    for sev in ['High', 'Medium', 'Low']:
        count = sev_counts.get(sev, 0)
        pct = (count / total_incidents) * 100
        print(f"   {sev:8s}: {count:6,} ({pct:5.1f}%)")

    # B. Link Locations to Incidents
    # Get unique (Incident, Location) pairs
    incident_locations = df[['incident_number', 'location']].dropna().drop_duplicates()
    
    # Merge Severity info onto Locations
    location_risk_df = pd.merge(incident_locations, incident_max_severity[['incident_number', 'Highest_Severity']], on='incident_number', how='inner')

    # -------------------------------------------------------------------------
    # 2. Top 10 Locations Analysis
    # -------------------------------------------------------------------------
    top_10_locs = location_risk_df['location'].value_counts().head(10).index.tolist()
    
    print(f"\nTop 10 locations for analysis:")
    for i, loc in enumerate(top_10_locs, 1):
        count = len(location_risk_df[location_risk_df['location'] == loc])
        print(f"   {i}. {loc}")

    # Filter data to top 10
    top_loc_df = location_risk_df[location_risk_df['location'].isin(top_10_locs)]

    # Create Crosstab: Location vs Severity
    risk_crosstab = pd.crosstab(top_loc_df['location'], top_loc_df['Highest_Severity'], normalize='index') * 100
    
    # Ensure all columns exist
    for col in ['High', 'Medium', 'Low']:
        if col not in risk_crosstab.columns:
            risk_crosstab[col] = 0.0
    
    # Add Counts for detailed reporting
    count_crosstab = pd.crosstab(top_loc_df['location'], top_loc_df['Highest_Severity'])

    # Sort by High Severity % for plotting risk
    risk_crosstab = risk_crosstab.sort_values('High', ascending=True)

    # Print Table
    print(f"\n📊 SEVERITY DISTRIBUTION BY LOCATION:")
    print("="*80)
    print(f"{'Location':<30} {'High':<6} {'Medium':<6} {'Low':<6}")
    print("-" * 80)
    
    # Sort descending for table print
    print_table = risk_crosstab.sort_values('High', ascending=False)
    for loc, row in print_table.iterrows():
        print(f"{loc:<30} {row['High']:<6.1f} {row['Medium']:<6.1f} {row['Low']:<6.1f}")

    # -------------------------------------------------------------------------
    # 3. Visualization (100% Stacked Bar)
    # -------------------------------------------------------------------------
    plt.figure(figsize=(14, 10))
    
    locations = risk_crosstab.index
    low_pct = risk_crosstab['Low'].values
    med_pct = risk_crosstab['Medium'].values
    high_pct = risk_crosstab['High'].values
    
    y_pos = np.arange(len(locations))
    bar_width = 0.8
    
    # Define colors (Green -> Yellow -> Red logic)
    colors = ['#66c2a5', '#fdae61', "#d62e2e"] # Diverging palette style

    # Plot Low
    p1 = plt.barh(y_pos, low_pct, bar_width, label='Low Severity', color=colors[0], edgecolor='white')
    # Plot Medium (stacked on Low)
    p2 = plt.barh(y_pos, med_pct, bar_width, left=low_pct, label='Medium Severity', color=colors[1], edgecolor='white')
    # Plot High (stacked on Low+Medium)
    p3 = plt.barh(y_pos, high_pct, bar_width, left=low_pct+med_pct, label='High Severity', color=colors[2], edgecolor='white')

    plt.yticks(y_pos, [loc[:30] for loc in locations], fontsize=11)
    plt.xlabel('Percentage of Incidents (%)', fontsize=12, fontweight='bold')
    plt.ylabel('Location', fontsize=12, fontweight='bold')
    plt.title('Risk Assessment: Severity Distribution by Location (Top 10)', fontsize=16, fontweight='bold', pad=20)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3, fontsize=11)
    plt.grid(axis='x', alpha=0.3)
    plt.xlim(0, 100)

    # Add Labels
    for i, (l, m, h) in enumerate(zip(low_pct, med_pct, high_pct)):
        # Low label
        if l > 8: plt.text(l/2, i, f'{l:.0f}%', ha='center', va='center', color='white', fontweight='bold')
        # Medium label
        if m > 8: plt.text(l + m/2, i, f'{m:.0f}%', ha='center', va='center', color='white', fontweight='bold')
        # High label
        if h > 5: plt.text(l + m + h/2, i, f'{h:.0f}%', ha='center', va='center', color='white', fontweight='bold')

    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 4. Insights
    # -------------------------------------------------------------------------
    print(f"\n🚨 RISK ASSESSMENT INSIGHTS:")
    print("="*50)

    highest_risk_loc = risk_crosstab['High'].idxmax()
    highest_risk_val = risk_crosstab['High'].max()
    
    lowest_risk_loc = risk_crosstab['High'].idxmin()
    lowest_risk_val = risk_crosstab['High'].min()

    high_risk_total = len(top_loc_df[top_loc_df['location'] == highest_risk_loc])
    high_risk_count = count_crosstab.loc[highest_risk_loc, 'High'] if 'High' in count_crosstab.columns else 0
    
    low_risk_total = len(top_loc_df[top_loc_df['location'] == lowest_risk_loc])
    low_risk_count = count_crosstab.loc[lowest_risk_loc, 'Low'] if 'Low' in count_crosstab.columns else 0

    print(f"🔴 HIGHEST RISK LOCATION: {highest_risk_loc}")
    print(f"   • High severity incidents: {highest_risk_val:.1f}%")
    print(f"   • Total incidents: {high_risk_total}")
    print(f"   • High severity count: {high_risk_count}")
    
    print(f"\n🟢 LOWEST RISK LOCATION: {lowest_risk_loc}")
    print(f"   • High severity incidents: {lowest_risk_val:.1f}%")
    print(f"   • Total incidents: {low_risk_total:,}")
    print(f"   • Low severity count: {low_risk_count:,}")

    avg_high = risk_crosstab['High'].mean()
    print(f"\n📊 OVERALL SUMMARY:")
    print(f"   • Average high severity rate: {avg_high:.1f}%")
    print(f"   • Range of high severity rates: {lowest_risk_val:.1f}% - {highest_risk_val:.1f}%")
    print(f"   • Locations with >20% high severity: {len(risk_crosstab[risk_crosstab['High'] > 20])}")

    print(f"\n💡 PREVENTION IMPLICATIONS:")
    print("="*30)
    print("   • Focus enhanced security at high-risk locations")
    print("   • Prioritize rapid response teams for critical locations")
    print("   • Implement location-specific prevention programs")
    print("   • Monitor emerging high-risk areas for early intervention")

def plot_temporal_trends(df: pd.DataFrame):
    """
    Analyzes temporal patterns (Month, Quarter, Weekday, Day of Week) 
    of Hate Crime Incidents.
    
    Methodology:
    - Filters to UNIQUE INCIDENTS to prevent overcounting multi-offense events.
    - Extracts temporal features from 'incident_date'.
    """
    print("📅 TEMPORAL TRENDS ANALYSIS:")
    print("="*60)

    # -------------------------------------------------------------------------
    # 1. Data Preparation (Incident Level)
    # -------------------------------------------------------------------------
    if 'unique_incident_id' not in df.columns:
        df['unique_incident_id'] = df['ori'].astype(str) + '-' + df['incident_number'].astype(str)
        
    if 'incident_date' not in df.columns:
        print("Error: 'incident_date' column missing.")
        return

    # Create a deduplicated DataFrame for Temporal Analysis (One row per incident)
    # We only need the ID and the Date
    incident_df = df[['unique_incident_id', 'incident_date']].drop_duplicates().copy()
    
    # Ensure datetime
    incident_df['incident_date'] = pd.to_datetime(incident_df['incident_date'])

    # Feature Engineering
    incident_df['month_name'] = incident_df['incident_date'].dt.month_name()
    incident_df['quarter'] = incident_df['incident_date'].dt.quarter
    incident_df['day_of_week'] = incident_df['incident_date'].dt.day_name()
    incident_df['is_weekend'] = incident_df['day_of_week'].isin(['Saturday', 'Sunday'])
    incident_df['year'] = incident_df['incident_date'].dt.year
    
    total_incidents = len(incident_df)

    # Define Palette (consistent with your orange theme)
    # 0=Dark Orange, 1=Medium Orange
    PROCESSED_PALETTE = ['#e6550d', '#fdae6b', '#fee6ce'] 

    # -------------------------------------------------------------------------
    # 2. Aggregation
    # -------------------------------------------------------------------------
    # Monthly
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_counts = incident_df['month_name'].value_counts().reindex(month_order)

    # Quarterly
    quarterly = incident_df['quarter'].value_counts().sort_index()

    # Weekday vs Weekend
    weekend_data = incident_df['is_weekend'].value_counts()
    
    # Daily
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_counts = incident_df['day_of_week'].value_counts().reindex(day_order)

    # -------------------------------------------------------------------------
    # 3. Visualization
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Plot 1: Monthly Distribution (Line Chart)
    axes[0, 0].plot(range(12), monthly_counts.values, marker='o', color=PROCESSED_PALETTE[0], 
                    linewidth=2, alpha=0.8)
    axes[0, 0].set_xticks(range(12))
    axes[0, 0].set_xticklabels([m[:3] for m in month_order], rotation=45)
    axes[0, 0].set_ylabel('Number of Incidents', fontweight='bold')
    axes[0, 0].set_title('Monthly Hate Crime Distribution', fontsize=13, fontweight='bold')
    axes[0, 0].axhline(monthly_counts.mean(), color='green', linestyle='--', label='Average', linewidth=2)
    axes[0, 0].set_ylim(0, monthly_counts.max() * 1.1)
    axes[0, 0].legend()
    axes[0, 0].grid(axis='x', alpha=0.5)

    # Plot 2: Quarterly Distribution (Pie Chart)
    axes[0, 1].pie(quarterly.values, labels=[f'Q{q}' for q in quarterly.index], 
                   autopct='%1.1f%%', colors=sns.color_palette("Oranges", n_colors=4), 
                   startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'}, pctdistance=0.85)
    axes[0, 1].set_title('Quarterly Distribution', fontsize=13, fontweight='bold')

    # Plot 3: Weekday vs Weekend (Bar Chart)
    # Handle case if only weekdays or only weekends exist in data snippet
    wk_labels = ['Weekday', 'Weekend']
    wk_vals = [weekend_data.get(False, 0), weekend_data.get(True, 0)]
    
    axes[1, 0].bar(wk_labels, wk_vals, 
                   color=[PROCESSED_PALETTE[1], PROCESSED_PALETTE[0]], 
                   width=0.6)
    axes[1, 0].set_ylabel('Number of Incidents', fontweight='bold')
    axes[1, 0].set_title('Weekday vs Weekend Incidents', fontsize=13, fontweight='bold')
    axes[1, 0].set_ylim(0, max(wk_vals) * 1.2)
    
    for i, v in enumerate(wk_vals):
        pct = v / total_incidents * 100
        axes[1, 0].text(i, v + max(wk_vals) * 0.05, f'{v:,}\n({pct:.1f}%)', 
                        ha='center', fontweight='bold', fontsize=10)

    # Plot 4: Day of Week Pattern (Bar Chart)
    colors_days = [PROCESSED_PALETTE[1] if day not in ['Saturday', 'Sunday'] else PROCESSED_PALETTE[0] for day in day_order]

    axes[1, 1].bar(range(7), daily_counts.values, color=colors_days)
    axes[1, 1].set_xticks(range(7))
    axes[1, 1].set_xticklabels([d[:3] for d in day_order], rotation=45)
    axes[1, 1].set_ylabel('Number of Incidents', fontweight='bold')
    axes[1, 1].set_title('Incidents by Day of Week', fontsize=13, fontweight='bold')
    axes[1, 1].axhline(daily_counts.mean(), color='green', linestyle='--', label='Average', linewidth=2)
    axes[1, 1].legend()

    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 4. Insights
    # -------------------------------------------------------------------------
    print("\n📅 TEMPORAL PATTERNS REVEALED:")
    print(f"   • Peak Month: {monthly_counts.idxmax()} ({monthly_counts.max():,} incidents)")
    print(f"   • Busiest Quarter: Q{quarterly.idxmax()} ({quarterly.max():,} incidents)")
    print(f"   • Weekend Incidents: {weekend_data.get(True, 0):,} ({weekend_data.get(True, 0)/total_incidents*100:.1f}%)")
    print(f"   • Most Active Day: {daily_counts.idxmax()} ({daily_counts.max():,} incidents)")
    print("\n💡 These patterns are COMPLETELY HIDDEN in raw date data!")

def plot_offender_demographics(df: pd.DataFrame):
    """
    Analyzes Offender Demographics: Race, Ethnicity, Age (Adult/Juvenile).
    
    Methodology:
    - CRITICAL: Filters to UNIQUE INCIDENTS first.
    - Demographics are incident-level attributes; summing rows without deduplication 
      would result in massive overcounting.
    """
    print("👨‍👩‍👧‍👦 OFFENDER DEMOGRAPHICS ANALYSIS:")
    print("="*60)

    # -------------------------------------------------------------------------
    # 1. Data Preparation (Incident Level)
    # -------------------------------------------------------------------------
    if 'unique_incident_id' not in df.columns:
        df['unique_incident_id'] = df['ori'].astype(str) + '-' + df['incident_number'].astype(str)

    # Columns needed for analysis
    demo_cols = [
        'unique_incident_id', 'offender_race', 'offender_ethnicity', 
        'num_adult_offenders', 'num_juvenile_offenders', 
        'country_region', 'state_name'
    ]
    
    # Check for missing columns
    missing_cols = [c for c in demo_cols if c not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns for demographic analysis: {missing_cols}")
        return

    # Create Incident-Level DataFrame (Deduplicated)
    # We take the 'first' value for categorical/static fields and max for counts (assuming consistency)
    incident_df = df.groupby('unique_incident_id')[demo_cols[1:]].first().reset_index()
    
    total_incidents = len(incident_df)
    
    # -------------------------------------------------------------------------
    # 2. Race & Ethnicity Analysis
    # -------------------------------------------------------------------------
    # Race
    race_counts = incident_df['offender_race'].value_counts().dropna()
    total_race_records = race_counts.sum()
    
    print(f"Total incidents with known offender race: {total_race_records:,} ({total_race_records/total_incidents*100:.1f}%)")
    print("\nOffender race breakdown:")
    for race, count in race_counts.items():
        pct = (count / total_race_records) * 100
        print(f"   {race:30s}: {count:6,} ({pct:5.1f}%)")

    # Ethnicity
    ethnicity_counts = incident_df['offender_ethnicity'].value_counts().dropna()
    total_ethnicity_records = ethnicity_counts.sum()
    
    print(f"\n📊 OFFENDER ETHNICITY DISTRIBUTION:")
    print("-" * 45)
    for ethnicity, count in ethnicity_counts.items():
        pct = (count / total_ethnicity_records) * 100
        print(f"   {ethnicity:30s}: {count:6,} ({pct:5.1f}%)")

    # -------------------------------------------------------------------------
    # 3. Adult vs Juvenile Analysis
    # -------------------------------------------------------------------------
    # Note: These columns might be NaN, fill with 0 for calculation
    adult_offenders = incident_df['num_adult_offenders'].fillna(0).sum()
    juvenile_offenders = incident_df['num_juvenile_offenders'].fillna(0).sum()
    total_offenders = adult_offenders + juvenile_offenders

    # Calculate percentages for insights later
    adult_pct = 0
    juvenile_pct = 0
    if total_offenders > 0:
        adult_pct = (adult_offenders / total_offenders) * 100
        juvenile_pct = (juvenile_offenders / total_offenders) * 100

    print(f"\n👨‍👩‍👧‍👦 AGE GROUP ANALYSIS:")
    print("-" * 50)
    if total_offenders > 0:
        print(f"Total offenders identified: {int(total_offenders):,}")
        print(f"Adult offenders:    {int(adult_offenders):,} ({adult_pct:.1f}%)")
        print(f"Juvenile offenders: {int(juvenile_offenders):,} ({juvenile_pct:.1f}%)")
    else:
        print("No offender age data available.")

    # -------------------------------------------------------------------------
    # 4. Visualizations
    # -------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(20, 12))
    fig.suptitle('Offender Demographics in US Hate Crimes', fontsize=16, fontweight='bold')

    # Plot 1: Race Distribution (Bar)
    race_data = race_counts.head(8)
    axes[1, 0].bar(range(len(race_data)), race_data.values, color=plt.cm.Oranges(np.linspace(1, 0, len(race_data))))
    axes[1, 0].set_xticks(range(len(race_data)))
    axes[1, 0].set_xticklabels([r[:20] for r in race_data.index], rotation=45, ha='right')
    axes[1, 0].set_ylabel('Number of Incidents', fontsize=12, fontweight='bold')
    axes[1, 0].set_title('Offender Race Distribution', fontsize=14, fontweight='bold')
    
    for i, count in enumerate(race_data.values):
        axes[1, 0].text(i, count + (race_data.max()*0.02), f'{count:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Plot 2: Ethnicity (Pie)
    if not ethnicity_counts.empty:
        # Use a localized palette
        axes[0, 1].pie(ethnicity_counts.values, labels=ethnicity_counts.index, autopct='%1.1f%%',
                       colors=sns.color_palette("Oranges", n_colors=len(ethnicity_counts)), startangle=90)
        axes[0, 1].set_title('Offender Ethnicity Distribution', fontsize=14, fontweight='bold')

    # Plot 3: Adult vs Juvenile (Pie)
    if total_offenders > 0:
        sizes = [adult_offenders, juvenile_offenders]
        labels = ['Adult', 'Juvenile']
        colors = ['#e6550d', '#fdae6b'] # Dark orange, light orange
        axes[0, 0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, explode=(0, 0.1))
        axes[0, 0].set_title('Adult vs Juvenile Offenders', fontsize=14, fontweight='bold')

    # Plot 4: Juvenile Rates by Region (Bar)
    # Calculate regional stats on incident_df
    region_stats = incident_df.groupby('country_region').agg({
        'num_adult_offenders': 'sum',
        'num_juvenile_offenders': 'sum'
    }).reset_index()
    
    region_stats['total'] = region_stats['num_adult_offenders'] + region_stats['num_juvenile_offenders']
    region_stats['juvenile_rate'] = (region_stats['num_juvenile_offenders'] / region_stats['total'] * 100).fillna(0)
    
    # Sort for plotting and insights
    region_stats = region_stats.sort_values('juvenile_rate', ascending=False)
    
    # Filter out empty regions or Possessions if needed
    region_stats = region_stats[region_stats['total'] > 0]

    if not region_stats.empty:
        bars = axes[1, 1].bar(range(len(region_stats)), region_stats['juvenile_rate'],
                              color=plt.cm.Oranges(np.linspace(0.9, 0.4, len(region_stats))))
        axes[1, 1].set_xticks(range(len(region_stats)))
        axes[1, 1].set_xticklabels(region_stats['country_region'], rotation=45, ha='right')
        axes[1, 1].set_ylabel('Juvenile Offender Rate (%)', fontsize=12, fontweight='bold')
        axes[1, 1].set_title('Juvenile Offender Rates by Region', fontsize=14, fontweight='bold')
        
        for i, rate in enumerate(region_stats['juvenile_rate']):
            axes[1, 1].text(i, rate + 0.5, f'{rate:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 5. Race by Motivation Analysis (Heatmap)
    # -------------------------------------------------------------------------
    print(f"\n🎯 OFFENDER RACE BY BIAS MOTIVATION ANALYSIS:")
    print("-" * 55)

    # Need to link Incident Race to Incident Motivations.
    # 1. Get bias cols
    bias_cols = [col for col in df.columns if col.startswith('bias_motivation_')]
    
    if bias_cols and 'offender_race' in df.columns:
        # Melt raw df to get all motivations per ID
        motivations_long = df[['unique_incident_id'] + bias_cols].melt(
            id_vars='unique_incident_id', value_name='Motivation'
        ).dropna().drop_duplicates()
        
        # Merge with incident-level race
        race_mot_merged = pd.merge(
            motivations_long, 
            incident_df[['unique_incident_id', 'offender_race']], 
            on='unique_incident_id'
        )
        
        # Filter for top motivations and races
        top_mots = ['Anti-Black or African American', 'Anti-Jewish', 'Anti-Gay (Male)', 'Anti-Hispanic or Latino', 'Anti-Asian']
        filtered_rm = race_mot_merged[
            (race_mot_merged['Motivation'].isin(top_mots)) & 
            (race_mot_merged['offender_race'] != 'Unknown')
        ]
        
        if not filtered_rm.empty:
            pivot_rm = pd.crosstab(filtered_rm['Motivation'], filtered_rm['offender_race'])
            
            plt.figure(figsize=(12, 8))
            sns.heatmap(pivot_rm, annot=True, fmt='d', cmap='Oranges', cbar_kws={'label': 'Number of Incidents'})
            plt.title('Top Offender Races by Bias Motivation', fontsize=16, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()

    # -------------------------------------------------------------------------
    # 6. Juvenile Rates by State (Top 10)
    # -------------------------------------------------------------------------
    print(f"\n📍 STATE JUVENILE OFFENDER ANALYSIS:")
    
    state_stats = incident_df.groupby('state_name').agg({
        'num_adult_offenders': 'sum',
        'num_juvenile_offenders': 'sum',
        'unique_incident_id': 'count'
    }).rename(columns={'unique_incident_id': 'incidents'})
    
    state_stats['total_offenders'] = state_stats['num_adult_offenders'] + state_stats['num_juvenile_offenders']
    state_stats['juvenile_rate'] = (state_stats['num_juvenile_offenders'] / state_stats['total_offenders'] * 100).fillna(0)
    
    # Filter for states with significant data (e.g., > 50 incidents) to avoid skew
    # Getting top 10 states by VOLUME of incidents
    top_states_vol = state_stats.nlargest(10, 'incidents')
    
    # Plot
    plt.figure(figsize=(14, 8))
    # Sort by juvenile rate for the plot
    plot_data = top_states_vol.sort_values('juvenile_rate', ascending=True)
    
    plt.barh(range(len(plot_data)), plot_data['juvenile_rate'],
             color=plt.cm.Oranges(np.linspace(0.4, 0.9, len(plot_data))))
             
    plt.yticks(range(len(plot_data)), plot_data.index)
    plt.xlabel('Juvenile Offender Rate (%)', fontsize=12, fontweight='bold')
    plt.title('Juvenile Offender Rates in Top 10 States (by Incident Volume)', fontsize=16, fontweight='bold')
    
    for i, v in enumerate(plot_data['juvenile_rate']):
        plt.text(v + 0.2, i, f'{v:.1f}%', va='center', fontsize=10, fontweight='bold')
        
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()

    # -------------------------------------------------------------------------
    # 7. Key Insights & Prevention Implications
    # -------------------------------------------------------------------------
    print(f"\n💡 KEY OFFENDER DEMOGRAPHICS INSIGHTS:")
    print("="*50)
    
    if not race_counts.empty:
        top_race = race_counts.idxmax()
        top_race_pct = (race_counts.max() / total_race_records) * 100
        print(f"   • Dominant offender race: {top_race} ({top_race_pct:.1f}% of cases with race data)")
    
    if total_offenders > 0:
        print(f"   • Adult offenders: {adult_pct:.1f}% of all identified offenders")
        print(f"   • Juvenile offenders: {juvenile_pct:.1f}% of all identified offenders")
    
    if not region_stats.empty:
        # region_stats is already sorted desc by juvenile_rate
        highest_juv_region = region_stats.iloc[0]
        lowest_juv_region = region_stats.iloc[-1]
        print(f"   • Highest juvenile rate region: {highest_juv_region['country_region']} ({highest_juv_region['juvenile_rate']:.1f}%)")
        print(f"   • Lowest juvenile rate region: {lowest_juv_region['country_region']} ({lowest_juv_region['juvenile_rate']:.1f}%)")
    
    if not top_states_vol.empty:
        # Find the state with the max rate among the top volume states
        highest_state_row = top_states_vol.loc[top_states_vol['juvenile_rate'].idxmax()]
        print(f"   • State with highest juvenile offenders (of top 10): {highest_state_row.name} ({highest_state_row['juvenile_rate']:.1f}%)")

    print("\n🎯 PREVENTION IMPLICATIONS:")
    print("="*30)
    print("   • Focus youth intervention programs in high juvenile offender regions")
    print("   • Address racial disparities in offender demographics")
    print("   • Target prevention efforts toward dominant offender groups")
    print("   • Develop region-specific intervention strategies")
