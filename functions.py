def generar_redaccion(tipo, datos):
    """
    Recibe el tipo de formato (A, B, C, D) y un diccionario con los datos.
    Devuelve el texto formateado en prosa clínica.
    """
    if tipo == "Formato A: Atención Psicológica":
        texto = f"**{datos['nombre']}** ({datos['edad']} años).\n\n"
        texto += f"El paciente se encuentra en estado {datos['lotep']}. "
        texto += f"En la evaluación de funciones cognitivas se observa {datos['cognitivas']}. "
        texto += f"Clínicamente se reporta {datos['hallazgos']}. "
        texto += f"En la esfera afectiva muestra un ánimo {datos['afectiva']}, con insight {datos['insight']}. "
        texto += f"Se identifica una red de apoyo familiar {datos['red_apoyo']}."
        return texto

    elif tipo == "Formato B: Nota de Evolución (SOAP)":
        return f"""
**Identificación:** {datos['nombre']}, {datos['edad']} años.
**Patologías Base:** {datos['patologias']}

| Fase | Descripción |
| :--- | :--- |
| **S (Subjetivo)** | {datos['subjetivo']} |
| **O (Objetivo)** | LOTEP: {datos['lotep']}. {datos['objetivo']} |
| **A (Análisis)** | {datos['analisis']} |
| **P (Plan)** | {datos['plan']} |
"""
    # Aquí añadiremos C y D en el siguiente paso para no saturar el código
    return "Formato en construcción..."