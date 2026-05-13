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

extra_roles = ['Medical Imaging and Therapeutic Equipment Technicians',
 'Other non-medical support staff',
 'Dental Prosthetic Technicians',
 'Physiotherapy Technicians and Assistants',
 'Midwifery Personnel',
 'Medical Prosthetic Technicians',
 'Medical and Pathology Laboratory scientists',
 'Medical and Pathology Laboratory Technicians',
 'Optometrists and Ophthalmic Opticians',
 'Biomedical engineer',
 'Pharmaceutical Technicians and Assistants',
 'Ambulance Workers',
 'Health information systems personnel',
 'Personal care workers in health services n.e.c',
 'Epidemiologists',
 'Managerial staff',
 'Environmental and Occupational Health and Hygiene Professionals',
 'Dental Assistants and Therapists',
 'Dispensing Opticians',
 'Paramedical Practitioners',
 'Field Epidemiologists',
 'Environmental and Occupational Health Inspectors and Associates',
 'Medical Records and Health Information Technicians',
 'Pharmacists',
 'Other non-medical professional staff',
 'Medical Assistants',
 'Dentists',
 'Audiologists and Speech Therapists',
 'Engineering and maintenance staff'
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

role_translation_extra = {
    "Medical Imaging and Therapeutic Equipment Technicians":
        "Técnicos en imágenes médicas y equipos terapéuticos",

    "Other non-medical support staff":
        "Otro personal de apoyo no médico",

    "Dental Prosthetic Technicians":
        "Técnicos en prótesis dentales",

    "Physiotherapy Technicians and Assistants":
        "Técnicos y asistentes de fisioterapia",

    "Midwifery Personnel":
        "Personal de partería y obstetricia",

    "Medical Prosthetic Technicians":
        "Técnicos en prótesis médicas",

    "Medical and Pathology Laboratory scientists":
        "Científicos de laboratorio médico y patología",

    "Medical and Pathology Laboratory Technicians":
        "Técnicos de laboratorio médico y patología",

    "Optometrists and Ophthalmic Opticians":
        "Optometristas y ópticos oftálmicos",

    "Biomedical engineer":
        "Ingenieros biomédicos",

    "Pharmaceutical Technicians and Assistants":
        "Técnicos y asistentes farmacéuticos",

    "Ambulance Workers":
        "Trabajadores de ambulancia",

    "Health information systems personnel":
        "Personal de sistemas de información en salud",

    "Personal care workers in health services n.e.c":
        "Trabajadores de cuidado personal en servicios de salud",

    "Epidemiologists":
        "Epidemiólogos",

    "Managerial staff":
        "Personal gerencial",

    "Environmental and Occupational Health and Hygiene Professionals":
        "Profesionales de salud e higiene ambiental y ocupacional",

    "Dental Assistants and Therapists":
        "Asistentes y terapeutas dentales",

    "Dispensing Opticians":
        "Ópticos dispensadores",

    "Paramedical Practitioners":
        "Profesionales paramédicos",

    "Field Epidemiologists":
        "Epidemiólogos de campo",

    "Environmental and Occupational Health Inspectors and Associates":
        "Inspectores y asociados de salud ocupacional y ambiental",

    "Medical Records and Health Information Technicians":
        "Técnicos en registros médicos e información de salud",

    "Pharmacists":
        "Farmacéuticos",

    "Other non-medical professional staff":
        "Otro personal profesional no médico",

    "Medical Assistants":
        "Asistentes médicos",

    "Dentists":
        "Dentistas",

    "Audiologists and Speech Therapists":
        "Audiólogos y terapeutas del habla",

    "Engineering and maintenance staff":
        "Personal de ingeniería y mantenimiento",
}



def assign_segment(role):
    if role in primary_roles:
        return "Mercado primario"
    elif role in secondary_roles:
        return "Mercado secundario"
    else:
        return "Fuerza laboral adyacente / otras profesiones de salud"


df = load_data()

target_iso = [
    "ARG", "BOL", "CHL", "COL", "CRI", "CUB", "DOM", "ECU",
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
        st.markdown("\n".join([f"- {role_translation_extra.get(role, role)}" for role in extra_roles]))

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