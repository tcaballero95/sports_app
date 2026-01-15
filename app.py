import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# Read data from JSON files
with open('actividades.json', 'r') as f:
	actividades = json.load(f)

with open('recompensas.json', 'r') as f:
	recompensas = json.load(f)

def cargar_registro(path):
	try:
		with open(path, 'r') as f:
			return json.load(f)
	except json.JSONDecodeError:
		return []
	except FileNotFoundError:
		return []



def conteo_puntos(registro):
	return sum(item['puntos'] for item in registro)

# Centrar el layout usando CSS
st.set_page_config(page_title="Sports Activities Tracking App", layout="centered")
 
# Título principal
st.title("Sports Activities Tracking App")

# Tabs
tabs = st.tabs(["Overview", "Actividades", "Recompensas", "Registro"])

with tabs[0]:
	st.header("Overview")
	st.markdown(
		"""
		¡Bienvenido a la app de seguimiento deportivo de **Josse** & **Tomi**! ❤️
	
		Esta aplicación te ayudará a llevar un registro de tus actividades deportivas y a visualizar tu progreso a lo largo del tiempo.
	
		- **Acumula puntos** por cada actividad que registres.
		- **Canjea tus puntos** por recompensas 😊.
		"""
	)

	st.divider()

	registro_actividades = cargar_registro('registro_actividades.json')
	registro_recompensas = cargar_registro('registro_recompensas.json')

	total_puntos_actividades = conteo_puntos(registro_actividades)
	total_puntos_recompensas = conteo_puntos(registro_recompensas)
	puntos_actuales = total_puntos_actividades - total_puntos_recompensas
	cols = st.columns([0.7, 0.3])
	cont1 = cols[0].container(horizontal_alignment="left", vertical_alignment="top")
	cont2 = cols[1].container(horizontal_alignment="right", vertical_alignment="top")

	with cont1:
		# Calcular puntos acumulados por dia para los ultimos 7 dias
		puntos_7d = [
			(datetime.strptime(item['fecha'], "%Y-%m-%d").date(), item['puntos'])
			for item in registro_actividades
			if datetime.strptime(item['fecha'], "%Y-%m-%d") >= datetime.now() - timedelta(days=7)
		]
		puntos_7d_df = pd.DataFrame(puntos_7d, columns=['Fecha', 'Puntos']).set_index('Fecha')
		puntos_7d_df_daily = puntos_7d_df.groupby('Fecha').sum().reindex(
			pd.date_range(datetime.now().date() - timedelta(days=6), datetime.now().date()), fill_value=0
		)
		puntos_7d_df_daily.index = puntos_7d_df_daily.index.date  # Asegura que el índice sea solo date
		df_plot = puntos_7d_df_daily.reset_index()
		df_plot['tooltip'] = df_plot.apply(lambda row: f"{row['index'].strftime('%d %b')}<br>{int(row['Puntos'])} puntos", axis=1)
		fig = px.bar(
			df_plot,
			x='index',
			y='Puntos',
			labels={'Fecha': 'Fecha', 'Puntos': 'Puntos'},
			height=200,
			color_discrete_sequence=["#2E9145"],
			custom_data=['tooltip']
		)
		dias = pd.date_range(datetime.now().date() - timedelta(days=6), datetime.now().date())
		meses_esp = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
		ticktext = [d.strftime('%d ') + meses_esp[d.month-1] for d in dias]
		fig.update_traces(
			hovertemplate='%{customdata[0]}'
		)
		fig.update_layout(
			xaxis_tickformat='%d %b',
			xaxis_title=None,
			yaxis_title=None,
			bargap=0.2,
			margin=dict(t=0, b=0, l=0, r=0),
			title=None,
			xaxis=dict(
				tickmode='array',
				tickvals=[d.strftime('%Y-%m-%d') for d in dias],
				ticktext=ticktext
			)
		)
		st.plotly_chart(fig, width='stretch', config={"displayModeBar": False, "scrollZoom": False, "doubleClick": False})

	with cont2:
		st.markdown(f"""
			<div style='background: #d4edda; color: #155724; border-radius: 12px; padding: 1em 1.5em; border: 1px solid #c3e6cb; font-weight: 400; font-size: 1em; text-align: right; float: right; display: inline-block;'>
				Puntos acumulados:<br> <b>{puntos_actuales} puntos <b>
			</div>
		""", unsafe_allow_html=True)
	

with tabs[1]:
	st.header("Actividades")
	st.write("Aquí puedes ver y registrar tus actividades deportivas.")
	with st.expander("Listado de actividades disponibles", expanded=False):
		actividades_df = pd.DataFrame(list(actividades.items()), columns=["Actividad", "Puntos"]).set_index("Actividad")
		st.dataframe(
			actividades_df,
			column_config={
				"Actividad": st.column_config.Column(width="large"),
				"Puntos": st.column_config.Column(width="small")
			}
		)
		
	with st.form("registro_actividad_form", border=False):
		st.subheader("Registrar Nueva Actividad")
		nombre = st.selectbox("Quién realizó la actividad?", options=["Josse", "Tomi"])
		actividad = st.selectbox("Selecciona la actividad", list(actividades.keys()))
		fecha = st.date_input("Fecha de la actividad")
		submit_button = st.form_submit_button("Registrar Actividad")

		if submit_button:
			registro_actividades = cargar_registro('registro_actividades.json')
			puntos_obtenidos = actividades[actividad]
			# Registar en json registro_actividades
			registro_actividades.append({
				"nombre": nombre,
				"actividad": actividad,
				"fecha": fecha,
				"puntos": puntos_obtenidos
			})
			# Write back to JSON file
			with open('registro_actividades.json', 'w') as f:
				json.dump(registro_actividades, f, default=str, indent=4)
			st.success(f"Actividad '{actividad}' registrada para el {fecha}. Has obtenido {puntos_obtenidos} puntos.")
		

with tabs[2]:
	st.header("Recompensas")
	st.write("Consulta las recompensas disponibles y canjea tus puntos.")
	with st.expander("Listado de recompensas disponibles", expanded=False):
		recompensas_df = pd.DataFrame(list(recompensas.items()), columns=["Recompensa", "Costo en Puntos"]).set_index("Recompensa")
		st.dataframe(
			recompensas_df,
			column_config={
				"Recompensa": st.column_config.Column(width="large"),
				"Costo en Puntos": st.column_config.Column(width="small")
			}
		)

	with st.form("canjear_recompensa_form", border=False):
		st.subheader("Canjear Recompensa")
		recompensa = st.selectbox("Selecciona la recompensa", list(recompensas.keys()))
		submit_button = st.form_submit_button("Canjear Recompensa")
		if submit_button:
			registro_recompensas = cargar_registro('registro_recompensas.json')
			# Registar en json registro_recompensas
			registro_recompensas.append({
				"recompensa": recompensa,
				"costo": recompensas[recompensa]
			})
			# Write back to JSON file
			with open('registro_recompensas.json', 'w') as f:
				json.dump(registro_recompensas, f, default=str, indent=4)
			st.success(f"Recompensa '{recompensa}' canjeada exitosamente.")
		

with tabs[3]:
	st.header("Registro")
	st.write("Visualiza tus actividades realizadas")
	grupo = st.selectbox("Selecciona grupo", options=["Josse", "Tomi", "Ambos"])
	registro_actividades = cargar_registro('registro_actividades.json')
	if grupo != "Ambos":
		registro_actividades = [item for item in registro_actividades if item['nombre'] == grupo]
	if registro_actividades:
		registro_actividades_df = pd.DataFrame(registro_actividades)
		registro_actividades_df = registro_actividades_df.drop(columns=['nombre'])
		registro_actividades_df['fecha'] = pd.to_datetime(registro_actividades_df['fecha'])
		registro_actividades_df = registro_actividades_df.sort_values(by='fecha', ascending=False).set_index('fecha')
		registro_actividades_df.index = registro_actividades_df.index.date
		st.dataframe(
			registro_actividades_df,
			column_config={
				"nombre": st.column_config.Column("Nombre", width="small"),
				"actividad": st.column_config.Column("Actividad", width="medium"),
				"puntos": st.column_config.Column("Puntos", width="small"),
			}
		)
	else:
		st.info("No hay actividades registradas para el grupo seleccionado.")