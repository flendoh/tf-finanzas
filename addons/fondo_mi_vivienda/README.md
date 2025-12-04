# Módulo de Gestión Financiera - Fondo Mivivienda

## Descripción General
Este módulo permite la gestión y simulación de créditos hipotecarios bajo el esquema del Fondo Mivivienda. Facilita el cálculo automático del Bono del Buen Pagador (BBP), la generación de cronogramas de pagos y la evaluación de la capacidad de endeudamiento de los clientes.

## Flujo de Trabajo

### 1. Configuración de Datos Maestros
Antes de realizar simulaciones, es necesario configurar los datos base del sistema:

*   **Proyectos Inmobiliarios**: Registrar los proyectos disponibles, definiendo el valor de la vivienda y si califica como vivienda sostenible.
*   **Productos Financieros**: Definir las entidades financieras y sus condiciones (tasas de interés, plazos mínimos/máximos, seguros y gastos administrativos).

### 2. Registro de Clientes
Se debe registrar la información del cliente, prestando atención a los campos que afectan la elegibilidad para los bonos:
*   Ingreso financiero mensual.
*   Historial de apoyo habitacional (determina si puede recibir el BBP).
*   Elegibilidad para el BBP Integrador.

### 3. Creación de Expediente (Simulación)
El expediente es el núcleo del proceso. Al crear uno nuevo:
*   Seleccione el Cliente y el Proyecto Inmobiliario.
*   Seleccione la Entidad Financiera.
*   Ingrese la Cuota Inicial y el Plazo deseado.

El sistema calculará automáticamente:
*   **Valor de la Vivienda y BBP**: Se realizan las conversiones de moneda necesarias si el proyecto y el préstamo están en monedas diferentes.
*   **Monto a Financiar**: Valor Vivienda - Cuota Inicial - BBP + Gastos.

### 4. Generación del Cronograma
Una vez ingresados los datos, se puede generar el cronograma de pagos. El sistema soporta:
*   Periodos de gracia total (capitalización de intereses) y parcial (pago de intereses).
*   Cálculo de cuotas constantes (método francés).
*   Inclusión de seguros (desgravamen e inmueble) en la cuota.

### 5. Evaluación y Confirmación
El sistema valida automáticamente si el expediente cumple con las reglas del producto financiero:
*   Verificación de ingresos mínimos.
*   Validación de plazos permitidos.
*   Límites de periodo de gracia.

Si la validación es exitosa, el expediente pasa a estado "Califica". De lo contrario, se marca como "No Califica" y se detallan las razones.

## Asistencia Técnica y Cálculos

### Cálculo del Bono del Buen Pagador (BBP)
El BBP se determina en base al valor de la vivienda (convertido a la moneda de la compañía para la búsqueda en tablas normativas). Existen rangos definidos que otorgan diferentes montos base. Si el proyecto es sostenible o el cliente aplica al bono integrador, se suman los montos correspondientes según la normativa vigente.

### Conversión de Monedas
El módulo maneja entornos multi-moneda.
*   Los rangos del BBP siempre se evalúan en la moneda base de la compañía (ej. Soles).
*   Si el crédito es en Dólares, el sistema convierte los montos utilizando la tasa de cambio del día para los cálculos y reconvierte los resultados a la moneda del expediente para su visualización.

### TCEA (Tasa de Costo Efectivo Anual)
La TCEA se calcula utilizando el flujo de caja del cronograma (Monto a financiar vs. Cuotas mensuales) mediante iteración numérica para encontrar la tasa interna de retorno (TIR) mensual, que luego se anualiza.

### Reportes
Desde el expediente se puede exportar el cronograma de pagos en formato PDF para ser entregado al cliente.
