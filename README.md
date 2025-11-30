# Fondo Mivivienda - Módulo de Gestión Financiera

Este módulo permite gestionar simulaciones de créditos hipotecarios bajo el esquema del Fondo Mivivienda, incluyendo el cálculo del Bono del Buen Pagador (BBP) y BBP Integrador.

## Entidades

### `fondo_mi_vivienda.dossier` (Expediente)
| Campo | Tipo | Relación / Descripción |
| :--- | :--- | :--- |
| `name` | Char | Nombre del expediente (Requerido) |
| `estado` | Selection | Borrador / Hecho |
| `cliente_id` | Many2one | Relación con `res.partner` |
| `proyecto_id` | Many2one | Relación con `fondo_mi_vivienda.project` |
| `aplicar_a_bbp_integrador` | Boolean | Relacionado con cliente |
| `es_vivienda_sostenible` | Boolean | Relacionado con proyecto |
| `ha_recibido_apoyo_habitacional_antes` | Boolean | Relacionado con cliente |
| `total_bbp` | Monetary | Calculado (BBP Base + BBP Integrador) |
| `bbp_base_amount` | Monetary | Calculado según valor de vivienda |
| `producto_financiero_id` | Many2one | Relación con `fondo_mi_vivienda.financial_product` |
| `moneda_id` | Many2one | Relacionado con producto financiero |
| `tea` | Float | Tasa Efectiva Anual (Relacionado) |
| `tcea` | Float | Tasa de Costo Efectivo Anual (Calculado) |
| `tem` | Float | Tasa Efectiva Mensual (Relacionado) |
| `valor_vivienda` | Monetary | Relacionado con proyecto |
| `cuota_inicial` | Monetary | Monto de cuota inicial |
| `lineas_cronograma_cuota_ids` | One2many | Relación con `fondo_mi_vivienda.fee_schedule_line` |
| `plazo_meses` | Integer | Plazo del crédito en meses |
| `tipo_periodo_gracia` | Selection | Total / Parcial |
| `periodo_gracia_meses` | Integer | Número de meses de gracia |
| `cuota_mensual` | Float | Calculada |
| `monto_a_financiar` | Monetary | Calculado |
| `porcentaje_de_cuota_inicial` | Float | Calculado |
| `seguro_desgravamen_mensual` | Float | Relacionado con producto financiero |
| `seguro_de_inmueble_anual` | Float | Relacionado con producto financiero |
| `otros_gastos_iniciales` | Monetary | Relacionado con producto financiero |
| `active` | Boolean | Activo/Inactivo |

### `fondo_mi_vivienda.project` (Proyecto Vivienda)
| Campo | Tipo | Relación / Descripción |
| :--- | :--- | :--- |
| `name` | Char | Nombre del proyecto |
| `tipo_propiedad` | Selection | Casa / Departamento |
| `moneda_id` | Many2one | Relación con `res.currency` |
| `valor_vivienda` | Monetary | Precio de la vivienda |
| `es_vivienda_sostenible` | Boolean | Indicador de sostenibilidad |
| `calle` | Char | Dirección |
| `departamento` | Many2one | Relación con `res.country.state` |
| `ciudad` | Char | Ciudad |
| `estado` | Selection | Abierto / Cerrado |
| `active` | Boolean | Activo/Inactivo |
| `expediente_ids` | One2many | Relación con `fondo_mi_vivienda.dossier` |
| `expediente_count` | Integer | Computado |

### `fondo_mi_vivienda.financial_product` (Entidad Financiera)
| Campo | Tipo | Relación / Descripción |
| :--- | :--- | :--- |
| `name` | Char | Nombre de la entidad/producto |
| `moneda_id` | Many2one | Relación con `res.currency` |
| `tipo_tasa` | Selection | Nominal / Efectiva |
| `periodo_tasa_nominal` | Selection | Periodo de la TN |
| `capitalizacion_tasa_nominal` | Selection | Periodo de capitalización |
| `periodo_tasa_efectiva` | Selection | Periodo de la TE |
| `valor_tasa` | Float | Valor porcentual de la tasa |
| `tea` | Float | Tasa Efectiva Anual (Computada) |
| `tem` | Float | Tasa Efectiva Mensual (Computada) |
| `seguro_desgravamen_mensual` | Float | Porcentaje mensual |
| `seguro_de_inmueble_anual` | Float | Porcentaje anual |
| `otros_gastos_iniciales` | Monetary | Gastos administrativos/notariales |
| `active` | Boolean | Activo/Inactivo |

### `fondo_mi_vivienda.fee_schedule_line` (Línea de Cronograma)
| Campo | Tipo | Relación / Descripción |
| :--- | :--- | :--- |
| `periodo` | Integer | Número de cuota |
| `expediente_id` | Many2one | Relación con `fondo_mi_vivienda.dossier` |
| `moneda_id` | Many2one | Relación con `res.currency` |
| `saldo_inicial` | Float | Saldo al inicio del periodo |
| `amortizacion` | Float | Capital amortizado |
| `intereses` | Float | Intereses del periodo |
| `seguro_desgravamen` | Float | Monto de seguro desgravamen |
| `seguro_inmueble` | Float | Monto de seguro inmueble |
| `saldo_final` | Float | Saldo al final del periodo |
| `cuota_mensual` | Float | Total a pagar en el periodo |

### `res.partner` (Cliente - Extensión)
| Campo | Tipo | Relación / Descripción |
| :--- | :--- | :--- |
| `aplicar_a_bbp_integrador` | Boolean | Elegible para bono integrador |
| `ha_recibido_apoyo_habitacional_antes` | Boolean | Historial de apoyo |
| `moneda_id` | Many2one | Relación con `res.currency` |
| `ingreso_financiero` | Monetary | Ingresos mensuales |
| `gastos_financieros` | Monetary | Gastos mensuales |
| `deudas_financieras` | Monetary | Deudas mensuales |
| `expedientes_ids` | One2many | Relación con `fondo_mi_vivienda.dossier` |
| `expedientes_count` | Integer | Computado |
