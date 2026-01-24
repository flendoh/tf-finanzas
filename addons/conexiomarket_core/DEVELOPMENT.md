# Guía de Desarrollo: Sistema de Features (Capabilities)

Esta guía explica cómo añadir nuevas capacidades ("features") a la arquitectura de conectores de marketplace.

## Concepto

El sistema utiliza un patrón de **Feature Flags** para gestionar las diferencias entre marketplaces. No todos los marketplaces soportan las mismas operaciones (ej. algunos permiten descargar etiquetas de envío, otros no).

En lugar de comprobar `if backend_type == 'falabella'`, definimos capabilities semánticas como `feature_order_document` (Soporta Documentos de Orden).

## Paso a Paso: Añadir una Nueva Feature

### 1. Definir la Feature en el Core (`market_connector_core`)

Edita `addons/market_connector_core/models/account.py`. Añade un campo booleano computado y su valor por defecto en `_compute_features`.

```python
# addons/market_connector_core/models/account.py

class MarketAccount(models.Model):
    # ...
    
    feature_stock_sync = fields.Boolean(
        string="Sincronización de Stock",
        compute="_compute_features",
        help="Indica si este backend soporta la actualización de stock en tiempo real"
    )

    def _compute_features(self):
        """ Compute supported features based on backend type. """
        for account in self:
            account.feature_order_document = False
            account.feature_stock_sync = False  # <--- Valor por defecto
```

### 2. Implementar la Lógica en el Core o Módulo Base

Usa el flag para mostrar/ocultar botones o ejecutar código condicionalmente.

**Ejemplo en Vista (XML):**
```xml
<button name="action_sync_stock" 
        string="Sincronizar Stock" 
        invisible="not feature_stock_sync"/>
```

**Ejemplo en Modelo (Python):**
```python
def action_sync_stock(self):
    if not self.feature_stock_sync:
        raise UserError("Esta cuenta no soporta sincronización de stock.")
    # ... lógica ...
```

### 3. Habilitar la Feature en el Conector Específico

En el módulo del conector (ej. `market_connector_falabella_orders`), sobrescribe `_compute_features` para activar el flag si el backend lo soporta.

```python
# addons/market_connector_falabella_orders/models/account.py

class MarketAccount(models.Model):
    _inherit = 'market.account'

    def _compute_features(self):
        super()._compute_features()
        for account in self:
            if account.backend_type == 'falabella':
                account.feature_order_document = True
                account.feature_stock_sync = True  # <--- Habilitar aquí
```

### 4. Implementar los Componentes Necesarios

Si la feature requiere lógica de conexión, asegúrate de implementar los componentes correspondientes (Adapters, Services, etc.) para ese backend.

Por ejemplo, si habilitas `feature_stock_sync`, deberías tener un `stock.manager` o similar registrado para el backend `falabella`.

## Resumen de Features Existentes

| Feature | Descripción | Módulo |
|---------|-------------|--------|
| `feature_order_document` | Descarga de documentos (etiquetas, facturas) de la orden. | `market_connector_core` |
