import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:5000/api"


# Function to fetch energy records from the API
def get_energy_records():
    try:
        response = requests.get(f"{API_URL}/energy_records/")
        response.raise_for_status()  # Raise an exception for HTTP errors
        return pd.DataFrame(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch energy records: {e}")
        return pd.DataFrame()


def add_new_record(new_record_data):
    try:
        response = requests.post(f"{API_URL}/energy_records/", json=new_record_data)
        response.raise_for_status()
        st.success("Record added successfully.")
        # st.json(response.json())
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to add new record: {e.response.content}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")


def update_record(record_id, update_record_data):
    try:
        response = requests.put(
            f"{API_URL}/energy_record_detail/{record_id}", json=update_record_data
        )
        response.raise_for_status()
        st.success(f"Record ID {record_id} updated successfully.")
        # st.json(response.json())
    except requests.exceptions.HTTPError as e:
        try:
            error_response = e.response.json()  # Parse the JSON response
            error_message = error_response.get(
                "error", "Unknown error"
            )  # Get the 'error' value
            # If there are extra error messages, we concatenate them for display.
            if "messages" in error_response:
                if isinstance(error_response["messages"], dict):
                    # Flatten the list of error messages if it's a dictionary
                    messages = "; ".join(
                        [
                            f"{k}: {', '.join(v)}"
                            for k, v in error_response["messages"].items()
                        ]
                    )
                elif isinstance(error_response["messages"], list):
                    messages = "; ".join(
                        error_response["messages"]
                    )  # Join list of messages
                else:
                    messages = error_response["messages"]
                error_message += f" - Details: {messages}"
            st.error(f"Failed to update record: {error_message}")
        except ValueError:
            st.error(f"Failed to update record: {e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")


def delete_record(record_id):
    try:
        # Corrected the URL to match the API's expected endpoint
        response = requests.delete(f"{API_URL}/energy_record_detail/{record_id}")
        response.raise_for_status()
        st.success(f"Record ID {record_id} deleted successfully.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to delete record: {e.response.content}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")


def visualize_energy_contribution():
    # Visualize the contribution of different energy uses to the total
    # (space heating, space cooling, water heating, and cooking)

    df = get_energy_records()
    if not df.empty:
        fig = px.pie(
            df,
            names="energy_use_types",
            title="The total energy consumption of space heating, space cooling, water heating, and cooking",
            labels={"energy_use_types": "Energy Use Types"},
            hover_data={"energy_use_types": "%{percent}, Terajoule"},
            hole=0.3,
        )

        fig.update_layout(
            legend_title_text="Energy Use Types",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            height=600,
        )

        st.plotly_chart(fig)


def visualize_energy_by_country_and_type():
    # Visualize energy consumption by country for each energy use type
    df = get_energy_records()

    if not df.empty:
        fig = px.bar(
            df,
            x="countries",
            y="energy_consumption",
            color="energy_use_types",
            labels={"energy_consumption": "Energy Consumption (Terajoules)"},
            title="Energy Consumption by Country and Energy Use Type",
            height=600,
        )

        fig.update_layout(
            xaxis_title="Country",
            yaxis_title="Energy Consumption (Terajoules)",
            legend_title_text="Energy Use Types",
            barmode="stack",
        )

        st.plotly_chart(fig)


def visualize_energy_uses_by_country():
    # Visualize Total Energy Consumption by country for all energy use types, energy types, and years (2012 to 2021)

    df = get_energy_records()

    df = df.sort_values(by="energy_consumption")

    fig = px.bar(
        df,
        y="countries",
        x="energy_consumption",
        color="energy_consumption",
        hover_name="countries",
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Total Energy Consumption by Country (2012 to 2021)",
        labels={
            "countries": "Countries",
            "energy_consumption": "Total Energy Consumption (Terajoule)",
        },
        height=600,
    )

    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)


def visualize_energy_consumption_each_year():
    # Visualize different countries' energy consumption each year
    df = get_energy_records()

    if not df.empty:
        # Allow user to select a year
        selected_year = st.selectbox("Select a Year", df["year"].unique())

        # Filter DataFrame for the selected year
        df_selected_year = df[df["year"] == selected_year]

        fig = px.bar(
            df_selected_year,
            x="energy_consumption",
            y="countries",
            orientation="h",
            title=f"Total Energy Consumption by Country in {selected_year}",
            labels={"energy_consumption": "Energy Consumption (Terajoules)"},
            color="energy_consumption",
            color_continuous_scale=px.colors.sequential.Plasma,
        )

        # Customize the layout of the bar chart
        fig.update_layout(
            xaxis_title="Energy Consumption (Terajoules)",
            yaxis_title="Countries",
            coloraxis_colorbar=dict(title="Energy Consumption (Terajoules)"),
            height=600,
        )

        st.plotly_chart(fig)


def visualize_energy_consumption_over_time():
    # Visualize Energy Consumption Over the Years (2012 to 2021) by Country

    df = get_energy_records()

    if not df.empty:
        fig = px.scatter(
            df,
            x="year",
            y="energy_consumption",
            color="countries",
            size="energy_consumption",
            labels={
                "energy_consumption": "Energy Consumption (Terajoules)",
                "year": "Year",
            },
            title="Total Energy Consumption Over the Years (2012 to 2021) by Country",
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Energy Consumption (Terajoules)",
            legend_title_text="Countries",
            height=600,
        )

        st.plotly_chart(fig)


def main():
    st.set_page_config(layout="wide")

    # Centered title
    st.markdown(
        "<h1 style='text-align: center;'>Energy Data Dashboard</h1>",
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Introduction text
    st.write(
        """
        ##### Welcome to the Energy Data Dashboard! 🌐 
        ###### This dashboard provides insights into energy records, allowing you to explore and analyze energy consumption data.

        The dataset used in this dashboard is sourced from [Eurostat](https://ec.europa.eu/eurostat/databrowser/view/NRG_D_HHQ/default/table?lang=en). Visit the Eurostat website for more detailed information and additional exploration options.

        Take a closer look at energy consumption in different countries by exploring the different visualizations below. Click on the expanders to interact with the App:

        - **Add a New Energy Record**: Add new energy consumption records to the dataset.
        - **Update an Existing Energy Record**: Update the details of existing records.
        - **Delete an Existing Energy Record**: Remove records that are no longer needed.

        Use the visualizations to analyze energy consumption trends by country, energy type, and more.
        """
    )

    df = get_energy_records()

    if not df.empty and all(
        col in df.columns
        for col in [
            "countries",
            "energy_types",
            "energy_use_types",
            "units",
            "id",
            "energy_consumption",
        ]
    ):
        # Side Panel for Actions
        st.sidebar.header("Actions")
        action = st.sidebar.radio(
            "Select Action",
            [
                "Add Record",
                "Update Record",
                "Delete Record",
            ],
        )

        # Add a spacer between the rows
        st.markdown("<br>", unsafe_allow_html=True)

        # Graphs
        col1, col2 = st.columns(2)

        with col1:
            visualize_energy_contribution()

        with col2:
            visualize_energy_by_country_and_type()

        # Add a spacer between the rows
        st.markdown("<br>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)

        with col3:
            visualize_energy_consumption_each_year()

        with col4:
            visualize_energy_consumption_over_time()

        col5, col6 = st.columns(2)

        with col5:
            visualize_energy_uses_by_country()

        with col6:
            st.write("Dataset In Use")
            st.dataframe(df)

        if action == "Add Record":
            with st.sidebar.expander("Add a New Energy Record"):
                if df.empty:
                    st.error("No data available to retrieve unique column values.")
                else:
                    new_country = st.selectbox("Country name", df["countries"].unique())
                    new_energy_type = st.selectbox(
                        "Energy type code", df["energy_types"].unique()
                    )
                    new_energy_use = st.selectbox(
                        "Energy use type", df["energy_use_types"].unique()
                    )
                    new_unit = st.selectbox("Unit name", df["units"].unique())
                    new_year = st.text_input("Year", value="2023")
                    new_consumption = st.text_input("Energy consumption")

                    if st.button("Add Record"):
                        try:
                            new_record_data = {
                                "countries": new_country,
                                "energy_types": new_energy_type,
                                "energy_use_types": new_energy_use,
                                "units": new_unit,
                                "year": int(new_year),
                                "energy_consumption": float(new_consumption),
                            }
                            add_new_record(new_record_data)
                        except ValueError:
                            st.error(
                                "Invalid input for Year or Energy consumption. Please enter valid numbers."
                            )
        elif action == "Update Record":
            with st.sidebar.expander("Update an Existing Energy Record"):
                record_id = st.selectbox(
                    "Select a Record ID to Update:",
                    df["id"].tolist(),
                    key="update_select",
                )

                current_record_data = None
                try:
                    current_record_response = requests.get(
                        f"{API_URL}/energy_record_detail/{record_id}"
                    )
                    current_record_response.raise_for_status()
                    current_record_data = current_record_response.json()
                except requests.exceptions.HTTPError as e:
                    st.error(
                        f"Failed to fetch details for Record ID {record_id}: {e.response.content}"
                    )
                except requests.exceptions.RequestException as e:
                    st.error(f"Request failed: {e}")

                if current_record_data is not None:
                    # st.json(current_record_data)
                    update_country = st.selectbox(
                        "Updated Country name",
                        df["countries"].unique(),
                        index=df["countries"]
                        .unique()
                        .tolist()
                        .index(current_record_data["countries"]),
                    )
                    update_energy_type = st.selectbox(
                        "Updated Energy type code",
                        df["energy_types"].unique(),
                        index=df["energy_types"]
                        .unique()
                        .tolist()
                        .index(current_record_data["energy_types"]),
                    )
                    update_energy_use = st.selectbox(
                        "Updated Energy use type",
                        df["energy_use_types"].unique(),
                        index=df["energy_use_types"]
                        .unique()
                        .tolist()
                        .index(current_record_data["energy_use_types"]),
                    )
                    update_unit = st.selectbox(
                        "Updated Unit name",
                        df["units"].unique(),
                        index=df["units"]
                        .unique()
                        .tolist()
                        .index(current_record_data["units"]),
                    )
                    update_year = st.text_input(
                        "Updated Year", value=str(current_record_data["year"])
                    )
                    update_consumption = st.text_input(
                        "Updated Energy consumption",
                        value=str(current_record_data["energy_consumption"]),
                    )

                    if st.button("Update Record"):
                        try:
                            update_record_data = {
                                "countries": update_country,
                                "energy_types": update_energy_type,
                                "energy_use_types": update_energy_use,
                                "units": update_unit,
                                "year": int(update_year),
                                "energy_consumption": float(update_consumption),
                            }
                            update_record(record_id, update_record_data)
                        except ValueError:
                            st.error(
                                "Invalid input for Updated Year or Energy consumption. Please enter valid numbers."
                            )
        elif action == "Delete Record":
            with st.sidebar.expander("Delete an Existing Energy Record"):
                del_record_id = st.selectbox(
                    "Select a Record ID to Delete:",
                    df["id"].tolist(),
                    key="delete_select",
                )

                if st.button("Delete Record"):
                    delete_record(del_record_id)
    else:
        st.error(
            "Error: Data could not be retrieved or DataFrame is missing expected columns."
        )


if __name__ == "__main__":
    main()
