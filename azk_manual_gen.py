#!/usr/bin/env python3
"""Generador de manual PDF para azk_zkteco_attendance_v19"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUT = "/tmp/azk_zkteco_manual.pdf"

# ── Colores ────────────────────────────────────────────────────────────────
BLUE      = colors.HexColor("#1a73e8")
DARK      = colors.HexColor("#202124")
GREY      = colors.HexColor("#5f6368")
LIGHTGREY = colors.HexColor("#f1f3f4")
GREEN     = colors.HexColor("#34a853")
ORANGE    = colors.HexColor("#ea4335")
WHITE     = colors.white

# ── Estilos ────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

TITLE = S("Title2",
    fontSize=28, textColor=WHITE, alignment=TA_CENTER,
    fontName="Helvetica-Bold", spaceAfter=6)
SUBTITLE = S("Subtitle2",
    fontSize=14, textColor=WHITE, alignment=TA_CENTER,
    fontName="Helvetica", spaceAfter=4)
H1 = S("H1",
    fontSize=16, textColor=BLUE, fontName="Helvetica-Bold",
    spaceBefore=18, spaceAfter=8, borderPad=4)
H2 = S("H2",
    fontSize=12, textColor=DARK, fontName="Helvetica-Bold",
    spaceBefore=12, spaceAfter=6)
BODY = S("Body2",
    fontSize=10, textColor=DARK, fontName="Helvetica",
    spaceAfter=6, leading=16, alignment=TA_JUSTIFY)
NOTE = S("Note",
    fontSize=9, textColor=GREY, fontName="Helvetica-Oblique",
    spaceAfter=4, leading=14)
CODE = S("Code",
    fontSize=9, textColor=colors.HexColor("#003087"),
    fontName="Courier", backColor=LIGHTGREY,
    spaceAfter=6, leading=14, leftIndent=12, rightIndent=12,
    borderPad=6)
BULLET = S("Bullet2",
    fontSize=10, textColor=DARK, fontName="Helvetica",
    spaceAfter=4, leading=15, leftIndent=16, bulletIndent=6)


# ── Page callback ──────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawString(2*cm, 1.2*cm, "azk_zkteco_attendance_v19 — Manual de Usuario")
    canvas.drawRightString(w - 2*cm, 1.2*cm, f"Página {doc.page}")
    canvas.setStrokeColor(LIGHTGREY)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.5*cm, w - 2*cm, 1.5*cm)
    canvas.restoreState()


# ── Contenido ──────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
    )

    story = []

    # ── Portada ──
    w, h = A4
    story.append(Spacer(1, 2*cm))

    # Bloque azul portada
    cover_data = [[
        Paragraph("AZK ZKTeco Attendance", TITLE),
    ],[
        Paragraph("Manual de Usuario — Odoo 19", SUBTITLE),
    ],[
        Paragraph("Módulo: azk_zkteco_attendance_v19", SUBTITLE),
    ]]
    cover_table = Table(cover_data, colWidths=[14*cm])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [BLUE, BLUE, BLUE]),
        ("TOPPADDING", (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 1*cm))

    # Descripción breve
    story.append(Paragraph(
        "Este módulo permite importar registros de asistencia desde dispositivos biométricos "
        "ZKTeco directamente en Odoo, aplicando automáticamente la deducción de la hora de "
        "comida a los empleados que estuvieron presentes durante la pausa.",
        BODY
    ))
    story.append(Spacer(1, 0.5*cm))

    # Info box
    info = Table([[
        Paragraph("Versión: 19.0.1.0.0 &nbsp;&nbsp;|&nbsp;&nbsp; "
                  "Autor: Azkatech &nbsp;&nbsp;|&nbsp;&nbsp; "
                  "Licencia: OPL-1", NOTE)
    ]], colWidths=[14*cm])
    info.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHTGREY),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(info)

    story.append(PageBreak())

    # ── 1. Requisitos ──
    story.append(Paragraph("1. Requisitos e Instalación", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    story.append(Paragraph("<b>Dependencias Python</b>", H2))
    story.append(Paragraph(
        "El módulo requiere la biblioteca <b>pyzk</b> para comunicarse con los dispositivos ZKTeco. "
        "Se instala automáticamente en Odoo.sh gracias al archivo <code>requirements.txt</code> "
        "incluido en el módulo.",
        BODY
    ))
    story.append(Paragraph("requirements.txt:", NOTE))
    story.append(Paragraph("pyzk", CODE))

    story.append(Paragraph(
        "Si necesitas instalarlo manualmente en el servidor:", BODY))
    story.append(Paragraph(
        "pip install pyzk --break-system-packages", CODE))

    story.append(Paragraph("<b>Instalación del módulo en Odoo</b>", H2))
    story.append(Paragraph(
        "Primera instalación:", BODY))
    story.append(Paragraph(
        "odoo-bin -i azk_zkteco_attendance_v19 --stop-after-init --no-http", CODE))
    story.append(Paragraph(
        "Actualización tras cambios de código:", BODY))
    story.append(Paragraph(
        "odoo-bin -u azk_zkteco_attendance_v19 --stop-after-init --no-http", CODE))

    story.append(Spacer(1, 0.3*cm))

    # ── 2. Configuración de la máquina ──
    story.append(Paragraph("2. Configuración de la Máquina Biométrica", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    story.append(Paragraph(
        "Navega a: <b>Asistencias → Attendance Machine → Machine Configuration → Nuevo</b>",
        BODY
    ))
    story.append(Spacer(1, 0.3*cm))

    # Tabla campos
    campos = [
        ["Campo", "Descripción", "Ejemplo"],
        ["Machine", "Nombre identificativo de la máquina", "Solicoma Principal"],
        ["Machine IP/DNS", "Dirección IP o hostname de la ZKTeco", "192.168.1.100"],
        ["Port No", "Puerto TCP (por defecto 4370)", "4370"],
        ["Password", "Contraseña numérica (si aplica)", "12345"],
        ["Timeout", "Segundos de espera de conexión", "10"],
        ["Company", "Empresa a la que pertenece", "Mi Empresa"],
        ["Location", "Dirección / ubicación del dispositivo", "Oficina Central"],
        ["Auto create employee", "Crear empleado si no existe en Odoo", "Desactivado"],
    ]
    t = Table(campos, colWidths=[3.8*cm, 7*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHTGREY]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dadce0")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(
        "⚠️  La máquina ZKTeco debe ser accesible por red desde el servidor Odoo. "
        "Si está en una red local y Odoo en la nube, configura un túnel (ngrok, WireGuard, etc.).",
        NOTE
    ))

    story.append(Spacer(1, 0.5*cm))

    # ── 3. Deducción de comida ──
    story.append(Paragraph("3. Deducción Automática de Comida", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    story.append(Paragraph(
        "En la ficha de la máquina, pestaña <b>\"Deducción Comida\"</b>, encontrarás tres campos:",
        BODY
    ))

    campos2 = [
        ["Campo", "Descripción", "Valor recomendado"],
        ["Deducir Comida", "Activar/desactivar la deducción automática", "✓ Activado"],
        ["Horas de Comida", "Número de horas a restar del check-out", "1.0"],
        ["Hora de Comida (UTC)", "Hora de la pausa de comida en UTC\n(Marruecos verano UTC+1 → 13.0 = 14:00 local)", "13.0"],
    ]
    t2 = Table(campos2, colWidths=[3.8*cm, 7.5*cm, 3*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), GREEN),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHTGREY]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dadce0")),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("<b>Lógica de la deducción</b>", H2))
    story.append(Paragraph(
        "La hora de comida <b>solo se descuenta si el empleado estuvo presente durante la pausa</b>. "
        "La condición que debe cumplirse es:",
        BODY
    ))
    story.append(Paragraph(
        "check_in  &lt;  hora_comida_UTC  &lt;  check_out_máquina", CODE))

    # Tabla ejemplos
    story.append(Paragraph("Ejemplos:", H2))
    ej = [
        ["Empleado", "Entrada", "Salida máquina", "¿Deducción?", "Salida final"],
        ["MNIJEL SAID",      "07:47", "16:53 (local)", "✓ Sí",  "15:53 (local)"],
        ["HAR-CHBAB HAFIDA", "07:59", "09:18 (local)", "✗ No\n(salió antes)", "09:18 (local)"],
        ["AISSAOUI AICHA",   "07:59", "17:05 (local)", "✓ Sí",  "16:05 (local)"],
    ]
    t3 = Table(ej, colWidths=[3.8*cm, 2*cm, 3.2*cm, 2.2*cm, 3.1*cm])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHTGREY]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dadce0")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TEXTCOLOR", (3,1), (3,1), GREEN),
        ("TEXTCOLOR", (3,2), (3,2), ORANGE),
        ("TEXTCOLOR", (3,3), (3,3), GREEN),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        "Los tiempos mostrados en Odoo son en hora local (UTC+1 en verano, Marruecos). "
        "Internamente Odoo almacena todo en UTC.",
        NOTE
    ))

    story.append(Spacer(1, 0.5*cm))

    # ── 4. Descarga de asistencias ──
    story.append(Paragraph("4. Descarga de Asistencias", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    story.append(Paragraph("<b>Manual (desde la UI)</b>", H2))
    pasos = [
        "Attendance → Attendance Machine → Machine Configuration",
        "Abrir la ficha de la máquina",
        'Clic en el botón <b>"Download Attendance"</b>',
        "Se muestra una notificación con el resumen: <i>N registros importados, X check-ins, Y check-outs</i>",
    ]
    for i, p in enumerate(pasos, 1):
        story.append(Paragraph(f"<b>{i}.</b>  {p}", BULLET))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Automática (tarea programada)</b>", H2))
    story.append(Paragraph(
        "El módulo incluye una tarea cron <b>\"Download Attendance\"</b> que se ejecuta "
        "periódicamente para importar asistencias de todas las máquinas configuradas. "
        "Puedes ajustar la frecuencia en: <b>Ajustes → Técnico → Acciones planificadas</b>.",
        BODY
    ))

    story.append(Paragraph("<b>Comportamiento de la importación</b>", H2))
    reglas = [
        "Solo se importan registros <b>no duplicados</b> (verificación por dispositivo + timestamp).",
        "Se reimportan los últimos <b>3 días</b> antes del último registro importado para capturar tardíos.",
        "Los registros con fecha <b>futura</b> se ignoran.",
        "Si el empleado <b>no marcó salida</b> en la máquina, el campo check_out queda <b>vacío</b> (NULL). No se genera salida automática.",
        "Si el empleado ya tiene una asistencia abierta del <b>día anterior</b> sin salida, se crea una nueva entrada para el día actual sin cerrar la anterior.",
    ]
    for r in reglas:
        story.append(Paragraph(f"• {r}", BULLET))

    story.append(Spacer(1, 0.5*cm))

    # ── 5. Gestión de empleados ──
    story.append(Paragraph("5. Vinculación de Empleados", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    story.append(Paragraph(
        "Para que las asistencias se importen correctamente, cada empleado en Odoo debe tener "
        "su <b>Device ID</b> configurado (el número de usuario en la máquina ZKTeco).",
        BODY
    ))
    story.append(Paragraph(
        "Ve a: <b>Empleados → [Empleado] → Pestaña HR Settings → Device ID</b>",
        BODY
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("<b>Creación automática de empleados</b>", H2))
    story.append(Paragraph(
        "Si el campo <b>\"Auto create employee\"</b> está activado en la ficha de la máquina, "
        "los usuarios de la máquina que no tengan un empleado en Odoo serán creados "
        "automáticamente con el nombre que aparece en el dispositivo.",
        BODY
    ))
    story.append(Paragraph(
        "⚠️  Se recomienda desactivar esta opción en producción y vincular manualmente "
        "los empleados para evitar duplicados.",
        NOTE
    ))

    story.append(Spacer(1, 0.5*cm))

    # ── 6. Botones de acción ──
    story.append(Paragraph("6. Botones de Acción en la Máquina", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    botones = [
        ["Botón", "Función"],
        ["Download Attendance", "Descarga e importa las asistencias de la máquina a Odoo"],
        ["Test Connection",     "Verifica que Odoo puede conectarse a la máquina por red"],
        ["Clear Device Data",   "⚠️  Borra TODOS los registros almacenados en la máquina.\n"
                                "Usarlo solo después de confirmar que todo está importado en Odoo."],
    ]
    t4 = Table(botones, colWidths=[4.5*cm, 9.5*cm])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK),
        ("TEXTCOLOR", (0,0), (-1,0), WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHTGREY]),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dadce0")),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TEXTCOLOR", (0,3), (0,3), ORANGE),
    ]))
    story.append(t4)

    story.append(Spacer(1, 0.5*cm))

    # ── 7. Resolución de problemas ──
    story.append(Paragraph("7. Resolución de Problemas", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    problemas = [
        (
            "Connection timeout / No se conecta a la máquina",
            [
                "Verificar que la IP/puerto son correctos.",
                "La máquina debe ser accesible desde el servidor Odoo (ping, telnet).",
                "Revisar firewalls y reglas de red.",
                "El campo Last Error en la ficha muestra el detalle del error.",
            ]
        ),
        (
            "0 Checkins: 0 Checkouts en la notificación",
            [
                "Los registros ya existían en azk_machine_attendance (duplicados).",
                "Para reimportar: eliminar registros de hr_attendance y azk_machine_attendance para las fechas afectadas y volver a descargar.",
            ]
        ),
        (
            "La deducción no se aplica",
            [
                "Verificar que 'Deducir Comida' está activado en la ficha de la máquina.",
                "Verificar que 'Hora de Comida (UTC)' = 13.0 (para Marruecos verano).",
                "La deducción solo aplica si check_in < hora_comida < check_out.",
                "Empleados que salen antes del mediodía no reciben deducción (correcto).",
            ]
        ),
        (
            "ModuleNotFoundError: No module named 'zk'",
            [
                "Ejecutar: pip install pyzk --break-system-packages",
                "Reiniciar el servidor Odoo (o push un commit vacío en Odoo.sh para forzar rebuild).",
            ]
        ),
        (
            "Empleado no encontrado / no se importa",
            [
                "Verificar que el empleado tiene el campo Device ID configurado.",
                "El Device ID debe coincidir con el user_id en la máquina ZKTeco.",
                "Activar 'Auto create employee' para crear empleados automáticamente (solo en pruebas).",
            ]
        ),
    ]

    for titulo, items in problemas:
        story.append(Paragraph(f"<b>⚠  {titulo}</b>", H2))
        for item in items:
            story.append(Paragraph(f"→  {item}", BULLET))
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.5*cm))

    # ── 8. Comandos útiles ──
    story.append(Paragraph("8. Comandos Útiles (Shell Odoo.sh)", H1))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE, spaceAfter=10))

    cmds = [
        ("Instalar el módulo (primera vez)",
         "odoo-bin -i azk_zkteco_attendance_v19 --stop-after-init --no-http"),
        ("Actualizar el módulo (tras cambios)",
         "odoo-bin -u azk_zkteco_attendance_v19 --stop-after-init --no-http"),
        ("Ver logs en tiempo real",
         "tail -f /home/odoo/logs/odoo.log"),
        ("Buscar errores del módulo",
         "grep -i 'azk_zkteco\\|LUNCH_DBG\\|ERROR' /home/odoo/logs/odoo.log | tail -50"),
        ("Eliminar asistencias de una fecha para reimportar",
         "psql -c \"DELETE FROM hr_attendance WHERE check_in >= '2026-07-16';\"\n"
         "psql -c \"DELETE FROM azk_machine_attendance WHERE date(punching_time) >= '2026-07-16';\""),
        ("Verificar configuración de la máquina en BD",
         "psql -c \"SELECT name, lunch_auto_deduction, lunch_deduction_hours, lunch_hour_utc FROM azk_machine;\""),
        ("Ver asistencias importadas hoy",
         "psql -c \"SELECT e.name, a.check_in, a.check_out FROM hr_attendance a \"\n"
         "       \"JOIN hr_employee e ON e.id=a.employee_id WHERE a.check_in::date=CURRENT_DATE;\""),
    ]

    for desc, cmd in cmds:
        story.append(Paragraph(f"<b>{desc}</b>", H2))
        story.append(Paragraph(cmd, CODE))

    # ── Pie final ──
    story.append(PageBreak())
    story.append(Spacer(1, 3*cm))
    fin_data = [[Paragraph(
        "azk_zkteco_attendance_v19<br/>"
        "<font size=10 color='#5f6368'>Módulo de Asistencias Biométricas ZKTeco para Odoo 19</font><br/><br/>"
        "<font size=9 color='#5f6368'>Desarrollado por Azkatech &nbsp;|&nbsp; Licencia OPL-1</font>",
        ParagraphStyle("fin", fontSize=18, textColor=BLUE,
                       fontName="Helvetica-Bold", alignment=TA_CENTER, leading=28)
    )]]
    fin_t = Table(fin_data, colWidths=[14*cm])
    fin_t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHTGREY),
        ("TOPPADDING", (0,0), (-1,-1), 30),
        ("BOTTOMPADDING", (0,0), (-1,-1), 30),
        ("ROUNDEDCORNERS", [12]),
    ]))
    story.append(fin_t)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF generado: {OUTPUT}")


if __name__ == "__main__":
    build()
