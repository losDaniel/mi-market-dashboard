import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard de Mercado",
    layout="wide"
)

st.title("Dashboard de Mercado: Entrevista Motivacional + Reducción de Daños")
st.caption("Estimación de fuerza laboral alcanzable por país, segmento y profesión")

DATA_PATH = "data/medical professionals in the americas latest year of data — WHO - latest_year.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    df = df[df["ISO3"] != "BRA"].copy()

    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    # -----------------------------
    # Roles incluidos en el análisis
    # -----------------------------

    included_roles = (
        primary_roles
        + secondary_roles
        + adjacent_roles
    )

    # Filtrar solamente profesiones relevantes
    df = df[df["Lvl1_name"].isin(included_roles)].copy()

    return df

country_name_to_iso = {
    "Perú": "PER",
    "Argentina": "ARG",
    "Bolivia": "BOL",
    "Chile": "CHL",
    "Colombia": "COL",
    "Costa Rica": "CRI",
    "Cuba": "CUB",
    "Republica Dominicana": "DOM",
    "Ecuador": "ECU",
    "El Salvador": "SLV",
    "España": "ESP",
    "Guatemala": "GTM",
    "Honduras": "HND",
    "Mexico": "MEX",
    "Nicaragua": "NIC",
    "Panama": "PAN",
    "Paraguay": "PRY",
    "Puerto Rico": "PRI",
    "Uruguay": "URY",
    "Venezuela": "VEN",
    "Estados Unidos Continental": "USA",
}


primary_roles = [
    "Psychologists",
    "Medical Doctors",
    "Nursing Personnel",
    "Community Health Workers",
    "Social work and counselling professionals",
    "Physiotherapists",
    "Nutritionists",
    "Dieticians",
]

secondary_roles = [
    "Social work associate professionals",
    "Personal care workers",
    "Health Care Assistants",
    "Home-based Personal Care Workers",
    "Traditional and Complementary Medicine Professionals",
    "Traditional and Complementary Medicine Associate Professionals",
]

adjacent_roles = [
    "Physiotherapy Technicians and Assistants",
    "Midwifery Personnel",
    "Optometrists and Ophthalmic Opticians",
    "Dental Assistants and Therapists",
    "Paramedical Practitioners",
    "Medical Assistants",
    "Dentists",
    "Audiologists and Speech Therapists",
]


role_translation = {
    "Psychologists": "Psicólogos",
    "Medical Doctors": "Médicos",
    "Nursing Personnel": "Personal de enfermería",
    "Community Health Workers": "Trabajadores comunitarios de salud",
    "Social work and counselling professionals": "Trabajo social y consejería",
    "Physiotherapists": "Fisioterapeutas",
    "Nutritionists": "Nutricionistas",
    "Dieticians": "Dietistas",
    "Social work associate professionals": "Técnicos/asociados de trabajo social",
    "Personal care workers": "Trabajadores de cuidado personal",
    "Health Care Assistants": "Asistentes de salud",
    "Home-based Personal Care Workers": "Cuidadores domiciliarios",
    "Traditional and Complementary Medicine Professionals": "Medicina tradicional y complementaria",
    "Traditional and Complementary Medicine Associate Professionals": "Técnicos de medicina tradicional y complementaria",
}

adjacent_role_translation = {
    "Physiotherapy Technicians and Assistants":
        "Técnicos y asistentes de fisioterapia",

    "Midwifery Personnel":
        "Personal de partería y obstetricia",

    "Optometrists and Ophthalmic Opticians":
        "Optometristas y ópticos oftálmicos",

    "Dental Assistants and Therapists":
        "Asistentes y terapeutas dentales",

    "Paramedical Practitioners":
        "Profesionales paramédicos",

    "Medical Assistants":
        "Asistentes médicos",

    "Dentists":
        "Dentistas",

    "Audiologists and Speech Therapists":
        "Audiólogos y terapeutas del habla",
}


@st.cache_data
def load_psychologist_range_data():
    psych_df = pd.read_csv(
        "data/Market Size — RDP.csv",
        encoding="latin1"
    )

    psych_df = psych_df[['Pais','Region','Poblacion','Psicologos Practicantes']]

    psych_df.columns = [
        "pais",
        "region",
        "poblacion",
        "psicologos_practicantes"
    ]

    psych_df["pais"] = psych_df["pais"].ffill()
    psych_df["region"] = psych_df["region"].astype(str).str.strip()

    psych_df = psych_df[psych_df["region"] == "Nacional"].copy()

    psych_df["poblacion"] = (
        psych_df["poblacion"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .replace({"": pd.NA})
        .astype(float)
    )


    psych_df["psicologos_practicantes"] = (
        psych_df["psicologos_practicantes"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .replace({"": pd.NA, "nan": pd.NA})
        .replace({pd.NA: None})
        .astype(float)
    )
#     psych_dt = psych_dt.where(pd.notnull(df), None)

    psych_df["ISO3"] = psych_df["pais"].str.strip().map(country_name_to_iso)
    psych_df = psych_df[psych_df["ISO3"].notna()].copy()

    # Model missing psychologist counts
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor

    psych_df["log_poblacion"] = np.log(psych_df["poblacion"])

    train = psych_df[psych_df["psicologos_practicantes"].notna()]
    missing = psych_df[psych_df["psicologos_practicantes"].isna()]

    # st.write('train')
    # st.write(train)
    # st.write('missing')
    # st.write(missing)

    features = ["poblacion", "log_poblacion"]

    model = RandomForestRegressor(
        n_estimators=500,
        random_state=42,
        min_samples_leaf=2
    )

    model.fit(train[features], train["psicologos_practicantes"])

    psych_df["psicologos_rango_alto"] = psych_df["psicologos_practicantes"]

    psych_df.loc[
        psych_df["psicologos_practicantes"].isna(),
        "psicologos_rango_alto"
    ] = model.predict(missing[features])

    psych_df["psicologos_rango_alto"] = (
        psych_df["psicologos_rango_alto"].round().astype(int)
    )

    return psych_df[["ISO3", "pais", "poblacion", "psicologos_practicantes", "psicologos_rango_alto"]]




def assign_segment(role):
    if role in primary_roles:
        return "Mercado primario"
    elif role in secondary_roles:
        return "Mercado secundario"
    else:
        return "Fuerza laboral adyacente / otras profesiones de salud"


psych_range_df = load_psychologist_range_data()

df = load_data()

target_iso = [
    "ARG", "BOL", "CHL", "COL", "CRI", "CUB", "DOM", "ECU", "ESP", 
    "SLV", "GTM", "HND", "MEX", "NIC", "PAN", "PRY", "PER", "URY", "VEN"
]

market_df = df[df["ISO3"].isin(target_iso)].copy()

market_df["segmento_mercado"] = market_df["Lvl1_name"].apply(assign_segment)
market_df["profesion"] = market_df["Lvl1_name"].replace(role_translation)

latest_df = (
    market_df.sort_values("Year")
    .groupby(["ISO3", "Country", "profesion", "Lvl2_name"], as_index=False)
    .tail(1)
)

who_psych_low = (
    latest_df[latest_df["profesion"] == "Psicólogos"]
    .groupby(["ISO3", "Country"], as_index=False)["Value"]
    .sum()
    .rename(columns={"Value": "psicologos_rango_bajo"})
)

psych_market_range = who_psych_low.merge(
    psych_range_df,
    on="ISO3",
    how="left"
)

psych_market_range["psicologos_rango_alto"] = psych_market_range[
    "psicologos_rango_alto"
].fillna(psych_market_range["psicologos_rango_bajo"])

psych_market_range["brecha"] = (
    psych_market_range["psicologos_rango_alto"]
    - psych_market_range["psicologos_rango_bajo"]
)



st.sidebar.header("Filtros")

selected_segments = st.sidebar.multiselect(
    "Segmento de mercado",
    sorted(latest_df["segmento_mercado"].dropna().unique()),
    default=sorted(latest_df["segmento_mercado"].dropna().unique())
)

selected_countries = st.sidebar.multiselect(
    "País",
    sorted(latest_df["Country"].dropna().unique()),
    default=sorted(latest_df["Country"].dropna().unique())
)

selected_professions = st.sidebar.multiselect(
    "Profesión",
    sorted(latest_df["profesion"].dropna().unique()),
    default=sorted(latest_df["profesion"].dropna().unique())
)

filtered_df = latest_df[
    latest_df["segmento_mercado"].isin(selected_segments)
    & latest_df["Country"].isin(selected_countries)
    & latest_df["profesion"].isin(selected_professions)
].copy()

segment_totals = (
    filtered_df.groupby("segmento_mercado", as_index=False)["Value"]
    .sum()
    .sort_values("Value", ascending=False)
)

country_totals = (
    filtered_df.groupby(["ISO3", "Country"], as_index=False)["Value"]
    .sum()
    .sort_values("Value", ascending=False)
)

profession_totals = (
    filtered_df.groupby(["profesion", "segmento_mercado"], as_index=False)["Value"]
    .sum()
    .sort_values("Value", ascending=False)
)

total_market = segment_totals["Value"].sum()
num_countries = filtered_df["Country"].nunique()
num_professions = filtered_df["profesion"].nunique()

tab1, tab2 = st.tabs(["Data OMS", "Data Nacional vs. OMS"])

with tab1: 

    col1, col2, col3 = st.columns(3)
    col1.metric("Fuerza laboral alcanzable estimada", f"{total_market:,.0f}")
    col2.metric("Países incluidos", f"{num_countries}")
    col3.metric("Profesiones incluidas", f"{num_professions}")

    st.divider()

    with st.expander("Ver definición de segmentos"):
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.subheader("Mercado primario")
            st.markdown("\n".join([f"- {role_translation.get(role, role)}" for role in primary_roles]))

        with col_b:
            st.subheader("Mercado secundario")
            st.markdown("\n".join([f"- {role_translation.get(role, role)}" for role in secondary_roles]))

        with col_c:
            st.subheader("Mercado adyacente")
            st.markdown("\n".join([f"- {adjacent_role_translation.get(role, role)}" for role in adjacent_roles]))

    st.subheader("Fuerza laboral alcanzable estimada por país")

    fig_country = px.bar(
        country_totals,
        x="Country",
        y="Value",
        title="Fuerza laboral alcanzable estimada por país",
        text_auto=".2s",
    )

    fig_country.update_layout(
        xaxis_title="País",
        yaxis_title="Profesionales estimados",
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig_country, use_container_width=True)

    st.subheader("Fuerza laboral estimada por segmento de mercado")

    fig_segment = px.bar(
        segment_totals,
        x="segmento_mercado",
        y="Value",
        title="Fuerza laboral estimada por segmento de mercado",
        text_auto=".2s",
    )

    fig_segment.update_layout(
        xaxis_title="Segmento de mercado",
        yaxis_title="Profesionales estimados",
    )

    st.plotly_chart(fig_segment, use_container_width=True)

    st.subheader("Principales profesiones alcanzables")

    fig_profession = px.bar(
        profession_totals.head(20),
        x="Value",
        y="profesion",
        color="segmento_mercado",
        orientation="h",
        title="Principales profesiones alcanzables",
        text_auto=".2s",
    )

    fig_profession.update_layout(
        xaxis_title="Profesionales estimados",
        yaxis_title="Profesión",
        legend_title_text="Segmento de mercado",
        yaxis={"categoryorder": "total ascending"},
    )

    st.plotly_chart(fig_profession, use_container_width=True)

    st.subheader("Distribución geográfica del mercado")

    fig_map = px.choropleth(
        country_totals,
        locations="ISO3",
        color="Value",
        hover_name="Country",
        title="Distribución geográfica de la fuerza laboral alcanzable estimada",
        color_continuous_scale="Blues",
    )

    fig_map.update_layout(
        coloraxis_colorbar_title="Profesionales estimados"
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("Composición del mercado por país, segmento y profesión")

    fig_tree = px.treemap(
        filtered_df,
        path=["Country", "segmento_mercado", "profesion"],
        values="Value",
        title="Composición del mercado por país, segmento y profesión",
    )

    st.plotly_chart(fig_tree, use_container_width=True)

    with st.expander("Ver tablas de datos"):
        st.write("Totales por segmento")
        st.dataframe(segment_totals, use_container_width=True)

        st.write("Totales por país")
        st.dataframe(country_totals, use_container_width=True)

        st.write("Totales por profesión")
        st.dataframe(profession_totals, use_container_width=True)

        st.write("Datos procesados")
        st.dataframe(filtered_df, use_container_width=True)

with tab2: 


    # # -----------------------------
    # # Comparación: psicólogos nacionales/modelados vs OMS
    # # -----------------------------

    st.header("Comparación de datos de psicólogos")
    st.caption(
        "Comparación entre datos nacionales disponibles, estimaciones propias por modelo y estimaciones reportadas por la OMS."
    )

    psych_df = psych_range_df.copy()

    psych_df["psicologos_practicantes"] = pd.to_numeric(
        psych_df["psicologos_practicantes"], errors="coerce"
    )

    psych_df["psicologos_rango_alto"] = pd.to_numeric(
        psych_df["psicologos_rango_alto"], errors="coerce"
    )

    psych_df["poblacion"] = pd.to_numeric(
        psych_df["poblacion"], errors="coerce"
    )

    psych_df["tipo_dato_nacional"] = psych_df["psicologos_practicantes"].notna().map({
        True: "Dato nacional disponible",
        False: "Estimación por modelo"
    })

    psych_df["valor_nacional_o_modelado"] = psych_df["psicologos_practicantes"].fillna(
        psych_df["psicologos_rango_alto"]
    )

    country_name_map = {
        "Perú": "Peru",
        "México": "Mexico",
        "Mexico": "Mexico",
        "Argentina": "Argentina",
        "Bolivia": "Bolivia (Plurinational State of)",
        "Chile": "Chile",
        "Colombia": "Colombia",
        "Costa Rica": "Costa Rica",
        "Cuba": "Cuba",
        "Republica Dominicana": "Dominican Republic",
        "Ecuador": "Ecuador",
        "El Salvador": "El Salvador",
        "España": "Spain",
        "Guinea Ecuatorial": "Equatorial Guinea",
        "Guatemala": "Guatemala",
        "Honduras": "Honduras",
        "Nicaragua": "Nicaragua",
        "Panama": "Panama",
        "Paraguay": "Paraguay",
        "Puerto Rico": "Puerto Rico",
        "Uruguay": "Uruguay",
        "Venezuela": "Venezuela (Bolivarian Republic of)",
        "Estados Unidos Continental": "United States of America",
    }

    psych_df["pais_oms"] = psych_df["pais"].replace(country_name_map)

    oms_psych = (
        latest_df[latest_df["profesion"].eq("Psicólogos")]
        .groupby(["Country", "ISO3"], as_index=False)["Value"]
        .sum()
        .rename(columns={
            "Country": "pais_oms",
            "Value": "psicologos_oms"
        })
    )

    compare_df = psych_df.merge(
        oms_psych[["pais_oms", "ISO3", "psicologos_oms"]],
        on="pais_oms",
        how="left"
    )

    compare_df["diferencia_vs_oms"] = (
        compare_df["valor_nacional_o_modelado"] - compare_df["psicologos_oms"]
    )

    compare_df["ratio_vs_oms"] = (
        compare_df["valor_nacional_o_modelado"] / compare_df["psicologos_oms"]
    )

    compare_df["psicologos_100k_nacional_modelado"] = (
        compare_df["valor_nacional_o_modelado"] / compare_df["poblacion"] * 100000
    )

    compare_df["psicologos_100k_oms"] = (
        compare_df["psicologos_oms"] / compare_df["poblacion"] * 100000
    )

    # -----------------------------
    # Métricas resumidas
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total nacional/modelado",
        f"{compare_df['valor_nacional_o_modelado'].sum():,.0f}"
    )

    col2.metric(
        "Total OMS disponible",
        f"{compare_df['psicologos_oms'].sum():,.0f}"
    )

    col3.metric(
        "Países comparados",
        f"{compare_df['pais'].nunique():,.0f}"
    )

    # -----------------------------
    # Filtro de países
    # -----------------------------

    selected_psych_countries = st.multiselect(
        "Países para comparar",
        sorted(compare_df["pais"].dropna().unique()),
        default=sorted(compare_df["pais"].dropna().unique())
    )

    compare_filtered = compare_df[
        compare_df["pais"].isin(selected_psych_countries)
    ].copy()

    # -----------------------------
    # 1. Barras: nacional/modelado vs OMS
    # -----------------------------

    plot_df = compare_filtered.melt(
        id_vars=["pais", "tipo_dato_nacional"],
        value_vars=["valor_nacional_o_modelado", "psicologos_oms"],
        var_name="fuente",
        value_name="psicologos"
    )

    plot_df["fuente"] = plot_df["fuente"].replace({
        "valor_nacional_o_modelado": "Fuente nacional / estimación propia",
        "psicologos_oms": "OMS"
    })

    plot_df = plot_df.dropna(subset=["psicologos"])

    fig_compare = px.bar(
        plot_df.sort_values("psicologos", ascending=False),
        x="pais",
        y="psicologos",
        color="fuente",
        barmode="group",
        pattern_shape="tipo_dato_nacional",
        title="Comparación de psicólogos estimados: fuentes nacionales, modelo propio y OMS",
        text_auto=".2s",
    )

    fig_compare.update_layout(
        xaxis_title="País",
        yaxis_title="Psicólogos / terapeutas estimados",
        legend_title="Fuente",
        xaxis_tickangle=-45,
    )

    st.plotly_chart(fig_compare, use_container_width=True)

    # -----------------------------
    # 2. Mapa: tamaño estimado del mercado
    # -----------------------------

    compare_filtered = compare_filtered.rename(columns={"ISO3_x":"ISO3"})

    fig_market_map = px.choropleth(
        compare_filtered,
        locations="ISO3",
        color="valor_nacional_o_modelado",
        hover_name="pais",
        hover_data={
            "valor_nacional_o_modelado": ":,.0f",
            "tipo_dato_nacional": True,
            "ISO3": False,
        },
        title="Distribución geográfica del mercado estimado de psicólogos",
        color_continuous_scale="Blues",
    )

    fig_market_map.update_layout(
        coloraxis_colorbar_title="Psicólogos estimados",
        margin=dict(t=60, l=20, r=20, b=20)
    )

    st.plotly_chart(fig_market_map, use_container_width=True)

    # -----------------------------
    # 5. Tabla comparativa
    # -----------------------------

    with st.expander("Ver tabla comparativa de psicólogos"):
        st.dataframe(
            compare_filtered[
                [
                    "pais",
                    "tipo_dato_nacional",
                    "poblacion",
                    "valor_nacional_o_modelado",
                    "psicologos_oms",
                    "diferencia_vs_oms",
                    "ratio_vs_oms",
                    "psicologos_100k_nacional_modelado",
                    "psicologos_100k_oms",
                ]
            ],
            use_container_width=True
        )