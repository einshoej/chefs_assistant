"""
Price estimation component for recipes
"""

import streamlit as st
from typing import Optional
from src.models.recipe import Recipe


def display_price_card(recipe: Recipe, language: str = 'no') -> None:
    """
    Display price estimation for a recipe

    Args:
        recipe: Recipe object with ingredient data
        language: Language for display ('no' for Norwegian, 'en' for English)
    """
    # Calculate estimated cost
    total_cost = recipe.estimate_cost()
    cost_per_serving = recipe.get_cost_per_serving()

    if total_cost <= 0:
        st.info("💰 Priser ikke tilgjengelige - ingredienspriser trengs" if language == 'no' else "💰 Price information not available - ingredient prices needed")
        return

    # Main price card
    with st.container(border=True):
        # Header
        st.markdown("### 💰 Kostnadsestimering" if language == 'no' else "### 💰 Cost Estimation")

        # Price metrics
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                label="Totalkostnad" if language == 'no' else "Total Cost",
                value=f"kr {total_cost:.0f}",
                help="Estimert totalkostnad for hele oppskriften" if language == 'no' else "Estimated total cost for entire recipe"
            )

        with col2:
            servings_text = "per porsjon" if language == 'no' else "per serving"
            st.metric(
                label=f"Kostnad {servings_text}",
                value=f"kr {cost_per_serving:.0f}",
                help="Estimert kostnad per porsjon" if language == 'no' else "Estimated cost per serving"
            )

        # Price category badge
        price_category = get_price_category(cost_per_serving)
        category_colors = {
            'budget': 'green',
            'moderate': 'orange',
            'expensive': 'red'
        }

        category_names = {
            'budget': 'Budsjett' if language == 'no' else 'Budget',
            'moderate': 'Moderat' if language == 'no' else 'Moderate',
            'expensive': 'Dyr' if language == 'no' else 'Expensive'
        }

        color = category_colors.get(price_category, 'gray')
        name = category_names.get(price_category, price_category)

        st.markdown(f":{color}[🏷️ {name}]")


def display_price_breakdown(recipe: Recipe, language: str = 'no') -> None:
    """
    Display detailed price breakdown by ingredient

    Args:
        recipe: Recipe object with ingredient data
        language: Language for display
    """
    with st.expander("💸 Kostnadsfordeling" if language == 'no' else "💸 Cost Breakdown"):

        breakdown_available = False

        for ingredient in recipe.recipe_ingredients:
            if ingredient.ingredient and ingredient.ingredient.price_info.average_price_per_kg > 0:
                breakdown_available = True

                # Rough cost calculation (simplified)
                price_per_kg = ingredient.ingredient.price_info.average_price_per_kg
                typical_weight = ingredient.ingredient.typical_weight_grams

                if typical_weight > 0:
                    ingredient_cost = (price_per_kg * typical_weight) / 1000

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {ingredient.get_ingredient_name(language)}")
                    with col2:
                        st.write(f"kr {ingredient_cost:.0f}")

        if not breakdown_available:
            st.info("Detaljert kostnadsfordeling ikke tilgjengelig" if language == 'no' else "Detailed cost breakdown not available")


def get_price_category(cost_per_serving: float) -> str:
    """
    Categorize price level based on cost per serving (NOK)

    Args:
        cost_per_serving: Cost per serving in NOK

    Returns:
        Price category: 'budget', 'moderate', or 'expensive'
    """
    if cost_per_serving <= 25:
        return 'budget'
    elif cost_per_serving <= 50:
        return 'moderate'
    else:
        return 'expensive'


def display_price_comparison(recipes: list[Recipe], language: str = 'no') -> None:
    """
    Display price comparison between multiple recipes

    Args:
        recipes: List of Recipe objects to compare
        language: Language for display
    """
    if len(recipes) < 2:
        return

    st.markdown("### 💰 Prissammenligning" if language == 'no' else "### 💰 Price Comparison")

    # Create comparison table
    import pandas as pd

    comparison_data = []
    for recipe in recipes[:5]:  # Limit to 5 recipes for display
        total_cost = recipe.estimate_cost()
        cost_per_serving = recipe.get_cost_per_serving()

        if total_cost > 0:
            price_category = get_price_category(cost_per_serving)
            comparison_data.append({
                'Oppskrift' if language == 'no' else 'Recipe': recipe.get_name(language),
                'Total (kr)': f"{total_cost:.0f}",
                'Per porsjon (kr)' if language == 'no' else 'Per serving (kr)': f"{cost_per_serving:.0f}",
                'Kategori' if language == 'no' else 'Category': price_category.title()
            })

    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def display_budget_badge(cost_per_serving: float, language: str = 'no') -> str:
    """
    Return budget badge markdown for recipe cards

    Args:
        cost_per_serving: Cost per serving in NOK
        language: Language for display

    Returns:
        Markdown string for badge
    """
    if cost_per_serving <= 0:
        return ""

    price_category = get_price_category(cost_per_serving)

    category_info = {
        'budget': {
            'color': 'green',
            'icon': '💚',
            'name': 'Budsjett' if language == 'no' else 'Budget'
        },
        'moderate': {
            'color': 'orange',
            'icon': '💛',
            'name': 'Moderat' if language == 'no' else 'Moderate'
        },
        'expensive': {
            'color': 'red',
            'icon': '💸',
            'name': 'Dyr' if language == 'no' else 'Expensive'
        }
    }

    info = category_info.get(price_category, {})
    color = info.get('color', 'gray')
    icon = info.get('icon', '💰')
    name = info.get('name', price_category.title())

    return f":{color}-badge[{icon} {name} - kr {cost_per_serving:.0f}]"


def display_weekly_budget_summary(recipes: list[Recipe], language: str = 'no') -> None:
    """
    Display budget summary for a week's worth of recipes

    Args:
        recipes: List of Recipe objects for the week
        language: Language for display
    """
    if not recipes:
        return

    total_weekly_cost = sum(recipe.estimate_cost() for recipe in recipes)

    if total_weekly_cost <= 0:
        return

    with st.container(border=True):
        st.markdown("### 📅 Ukens matbudsjett" if language == 'no' else "### 📅 Weekly Food Budget")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Total ukekostnad" if language == 'no' else "Total weekly cost",
                value=f"kr {total_weekly_cost:.0f}",
                help="Sum av alle oppskrifter denne uken" if language == 'no' else "Sum of all recipes this week"
            )

        with col2:
            daily_average = total_weekly_cost / 7
            st.metric(
                label="Snitt per dag" if language == 'no' else "Average per day",
                value=f"kr {daily_average:.0f}",
                help="Gjennomsnittlig daglig matkostnad" if language == 'no' else "Average daily food cost"
            )

        with col3:
            # Assume 2 people
            cost_per_person = total_weekly_cost / 2
            st.metric(
                label="Per person/uke" if language == 'no' else "Per person/week",
                value=f"kr {cost_per_person:.0f}",
                help="Kostnad per person for hele uken" if language == 'no' else "Cost per person for the entire week"
            )

        # Budget category for the week
        budget_levels = {
            (0, 200): ('green', 'Svært rimelig', 'Very budget-friendly'),
            (200, 400): ('green', 'Rimelig', 'Budget-friendly'),
            (400, 600): ('orange', 'Moderat', 'Moderate'),
            (600, 800): ('orange', 'Litt dyrt', 'Somewhat expensive'),
            (800, float('inf')): ('red', 'Dyrt', 'Expensive')
        }

        for (min_cost, max_cost), (color, name_no, name_en) in budget_levels.items():
            if min_cost <= total_weekly_cost < max_cost:
                name = name_no if language == 'no' else name_en
                st.markdown(f":{color}[🏷️ {name} matbudsjett]" if language == 'no' else f":{color}[🏷️ {name} food budget]")
                break