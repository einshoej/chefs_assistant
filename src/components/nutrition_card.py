"""
Nutrition information display component
"""

import streamlit as st
from typing import Optional
from src.models.recipe import Recipe
from src.models.ingredient import NutritionInfo


def display_nutrition_card(recipe: Recipe, language: str = 'no') -> None:
    """
    Display nutrition information for a recipe

    Args:
        recipe: Recipe object with ingredient data
        language: Language for display ('no' for Norwegian, 'en' for English)
    """
    # Calculate nutrition per serving
    nutrition = recipe.calculate_nutrition_per_serving()

    if not nutrition:
        st.info("Nutrition information not available - ingredient nutritional data needed")
        return

    # Main nutrition card
    with st.container(border=True):
        # Header
        servings_text = "per porsjon" if language == 'no' else "per serving"
        st.markdown(f"### 🍽️ Næringsinformasjon {servings_text}")

        # Primary macros in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Kalorier" if language == 'no' else "Calories",
                value=f"{nutrition.calories:.0f}",
                help="Totalt energiinnhold" if language == 'no' else "Total energy content"
            )

        with col2:
            st.metric(
                label="Protein" if language == 'no' else "Protein",
                value=f"{nutrition.protein:.1f}g",
                help="Proteiner for muskler og vekst" if language == 'no' else "Proteins for muscle and growth"
            )

        with col3:
            st.metric(
                label="Karbohydrater" if language == 'no' else "Carbs",
                value=f"{nutrition.carbs:.1f}g",
                help="Karbohydrater for energi" if language == 'no' else "Carbohydrates for energy"
            )

        with col4:
            st.metric(
                label="Fett" if language == 'no' else "Fat",
                value=f"{nutrition.fat:.1f}g",
                help="Fett for energi og vitaminer" if language == 'no' else "Fat for energy and vitamins"
            )

        # Additional nutrients
        if nutrition.fiber > 0 or nutrition.sugar > 0 or nutrition.sodium > 0:
            st.divider()

            col5, col6, col7 = st.columns(3)

            with col5:
                if nutrition.fiber > 0:
                    st.metric(
                        label="Fiber" if language == 'no' else "Fiber",
                        value=f"{nutrition.fiber:.1f}g",
                        help="Kostfiber for fordøyelsen" if language == 'no' else "Dietary fiber for digestion"
                    )

            with col6:
                if nutrition.sugar > 0:
                    st.metric(
                        label="Sukker" if language == 'no' else "Sugar",
                        value=f"{nutrition.sugar:.1f}g",
                        help="Naturlig og tilsatt sukker" if language == 'no' else "Natural and added sugar"
                    )

            with col7:
                if nutrition.sodium > 0:
                    st.metric(
                        label="Natrium" if language == 'no' else "Sodium",
                        value=f"{nutrition.sodium:.0f}mg",
                        help="Salt og natrium" if language == 'no' else "Salt and sodium"
                    )

        # Vitamins and minerals (if available)
        if nutrition.vitamins or nutrition.minerals:
            with st.expander("🧪 Vitaminer og mineraler" if language == 'no' else "🧪 Vitamins and Minerals"):

                if nutrition.vitamins:
                    st.markdown("**Vitaminer:**" if language == 'no' else "**Vitamins:**")
                    vitamins_cols = st.columns(min(3, len(nutrition.vitamins)))

                    for i, (vitamin, amount) in enumerate(nutrition.vitamins.items()):
                        col_idx = i % len(vitamins_cols)
                        with vitamins_cols[col_idx]:
                            st.write(f"• {vitamin}: {amount:.1f}")

                if nutrition.minerals:
                    st.markdown("**Mineraler:**" if language == 'no' else "**Minerals:**")
                    minerals_cols = st.columns(min(3, len(nutrition.minerals)))

                    for i, (mineral, amount) in enumerate(nutrition.minerals.items()):
                        col_idx = i % len(minerals_cols)
                        with minerals_cols[col_idx]:
                            st.write(f"• {mineral}: {amount:.1f}")


def display_macro_breakdown(nutrition: NutritionInfo) -> None:
    """
    Display macronutrient breakdown as a pie chart

    Args:
        nutrition: NutritionInfo object with macro data
    """
    if not nutrition or (nutrition.protein == 0 and nutrition.carbs == 0 and nutrition.fat == 0):
        return

    # Calculate calories from macros (approximation)
    protein_calories = nutrition.protein * 4  # 4 cal/g
    carb_calories = nutrition.carbs * 4       # 4 cal/g
    fat_calories = nutrition.fat * 9          # 9 cal/g

    total_macro_calories = protein_calories + carb_calories + fat_calories

    if total_macro_calories > 0:
        # Calculate percentages
        protein_pct = (protein_calories / total_macro_calories) * 100
        carb_pct = (carb_calories / total_macro_calories) * 100
        fat_pct = (fat_calories / total_macro_calories) * 100

        # Display as progress bars
        st.markdown("### Makronæringsstoffer" if st.session_state.get('language', 'no') == 'no' else "### Macronutrients")

        st.write(f"🍖 Protein: {protein_pct:.0f}%")
        st.progress(protein_pct / 100)

        st.write(f"🍞 Karbohydrater: {carb_pct:.0f}%" if st.session_state.get('language', 'no') == 'no' else f"🍞 Carbohydrates: {carb_pct:.0f}%")
        st.progress(carb_pct / 100)

        st.write(f"🥑 Fett: {fat_pct:.0f}%" if st.session_state.get('language', 'no') == 'no' == 'no' else f"🥑 Fat: {fat_pct:.0f}%")
        st.progress(fat_pct / 100)


def display_nutrition_comparison(recipes: list[Recipe], language: str = 'no') -> None:
    """
    Display nutrition comparison between multiple recipes

    Args:
        recipes: List of Recipe objects to compare
        language: Language for display
    """
    if len(recipes) < 2:
        return

    st.markdown("### 📊 Sammenligning av næring" if language == 'no' else "### 📊 Nutrition Comparison")

    # Create comparison table
    import pandas as pd

    comparison_data = []
    for recipe in recipes[:5]:  # Limit to 5 recipes for display
        nutrition = recipe.calculate_nutrition_per_serving()
        if nutrition:
            comparison_data.append({
                'Oppskrift' if language == 'no' else 'Recipe': recipe.get_name(language),
                'Kalorier' if language == 'no' else 'Calories': f"{nutrition.calories:.0f}",
                'Protein (g)': f"{nutrition.protein:.1f}",
                'Karbs (g)' if language == 'no' else 'Carbs (g)': f"{nutrition.carbs:.1f}",
                'Fett (g)' if language == 'no' else 'Fat (g)': f"{nutrition.fat:.1f}"
            })

    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def calculate_daily_nutrition_percentage(nutrition: NutritionInfo, language: str = 'no') -> dict:
    """
    Calculate percentage of daily recommended values

    Args:
        nutrition: NutritionInfo object
        language: Language for display

    Returns:
        Dictionary with daily value percentages
    """
    # Recommended daily values (approximate for adults)
    daily_values = {
        'calories': 2000,
        'protein': 50,      # grams
        'carbs': 300,       # grams
        'fat': 65,          # grams
        'fiber': 25,        # grams
        'sodium': 2300      # mg
    }

    percentages = {}

    if nutrition.calories > 0:
        percentages['calories'] = min((nutrition.calories / daily_values['calories']) * 100, 100)

    if nutrition.protein > 0:
        percentages['protein'] = min((nutrition.protein / daily_values['protein']) * 100, 100)

    if nutrition.carbs > 0:
        percentages['carbs'] = min((nutrition.carbs / daily_values['carbs']) * 100, 100)

    if nutrition.fat > 0:
        percentages['fat'] = min((nutrition.fat / daily_values['fat']) * 100, 100)

    if nutrition.fiber > 0:
        percentages['fiber'] = min((nutrition.fiber / daily_values['fiber']) * 100, 100)

    if nutrition.sodium > 0:
        percentages['sodium'] = min((nutrition.sodium / daily_values['sodium']) * 100, 100)

    return percentages


def display_daily_values(nutrition: NutritionInfo, language: str = 'no') -> None:
    """
    Display daily recommended value percentages

    Args:
        nutrition: NutritionInfo object
        language: Language for display
    """
    percentages = calculate_daily_nutrition_percentage(nutrition, language)

    if not percentages:
        return

    with st.expander("📈 Prosent av anbefalt daglig inntak" if language == 'no' else "📈 Percent Daily Values"):
        st.caption("Basert på en 2000 kalori diett" if language == 'no' else "Based on a 2000 calorie diet")

        for nutrient, pct in percentages.items():
            if pct > 0:
                # Color coding for daily values
                if pct <= 20:
                    color = "normal"
                elif pct <= 50:
                    color = "off"  # Orange-ish
                else:
                    color = "inverse"  # Red-ish for high values

                nutrient_names = {
                    'calories': 'Kalorier' if language == 'no' else 'Calories',
                    'protein': 'Protein',
                    'carbs': 'Karbohydrater' if language == 'no' else 'Carbohydrates',
                    'fat': 'Fett' if language == 'no' else 'Fat',
                    'fiber': 'Fiber',
                    'sodium': 'Natrium' if language == 'no' else 'Sodium'
                }

                st.metric(
                    label=nutrient_names.get(nutrient, nutrient.title()),
                    value=f"{pct:.0f}%",
                    delta=None
                )