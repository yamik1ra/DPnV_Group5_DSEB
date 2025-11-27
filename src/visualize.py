import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

import seaborn as sns
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
