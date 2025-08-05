# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Get user input for name
name_on_order = st.text_input('Name On Smoothie:')
st.write('The Name on your Smoothie will be:', name_on_order)

# Get active session and data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'), col('search_on'))
pd_df = my_dataframe.to_pandas()

# Create multiselect for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)


# Process the order
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ''
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    # Clean up the ingredients string
    ingredients_string = ingredients_string.strip()
    
    # Show what will be ordered
    st.write('**Your smoothie will contain:**', ingredients_string)
    
    # Submit button
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        # Validate that name is provided
        if name_on_order:
            try:
                # Fixed SQL statement - inserting both ingredients and name
                my_insert_stmt = f"""
                INSERT INTO smoothies.public.orders(ingredients, name_on_order) 
                VALUES ('{ingredients_string}', '{name_on_order}')
                """
                
                # Execute the insert
                session.sql(my_insert_stmt).collect()
                
                # Success message
                st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
                
            except Exception as e:
                st.error(f"Error placing order: {str(e)}")
        else:
            st.error("Please enter your name before submitting the order!")
else:
    st.info("Please select at least one ingredient for your smoothie.")
