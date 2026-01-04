# SPECIFICATION.md
1. Propósito

El Protocolo AEE (Anclaje de Evidencia Electrónica) define un mecanismo de preservación temprana para archivos digitales, orientado a fijar su estado técnico en un momento determinado del tiempo.

Su función es probar existencia, integridad y momento, sin realizar análisis forense ni emitir juicios periciales.

AEE constituye la Fase 0 de un pipeline probatorio más amplio.

2. Alcance

El protocolo AEE:

Captura el archivo en su estado original

Calcula un hash criptográfico (SHA-256)

Registra un timestamp UTC

Genera un registro técnico reproducible

Produce un certificado verificable

El protocolo AEE no:

Analiza contenido

Detecta manipulaciones visuales

Determina autoría

Sustituye pericias forenses

Emite conclusiones legales

3. Principios de diseño
3.1 Preservación temprana

El valor probatorio aumenta cuanto menor es la distancia temporal entre la creación/adquisición del archivo y su fijación técnica.

3.2 No intrusividad

El protocolo no modifica el archivo original ni introduce transformaciones sobre su contenido.

3.3 Reproducibilidad

Cualquier tercero debe poder verificar:

El hash

El algoritmo utilizado

El momento registrado

3.4 Neutralidad técnica

AEE no interpreta ni evalúa el significado del contenido preservado.

4. Flujo operativo (alto nivel)

Recepción del archivo

Cálculo de hash SHA-256

Obtención de timestamp UTC

Registro técnico estructurado

Emisión de certificado

5. Relación con otras disciplinas

AEE es complementario a:

Informática forense

Análisis pericial

Técnicas de similitud perceptual (pHash, DCT)

Estas disciplinas requieren un punto de partida confiable que AEE provee, pero no reemplaza.

6. Marco conceptual

El protocolo se alinea con prácticas aceptadas de preservación de evidencia digital, incluyendo principios doctrinarios de fijación temprana y cadena de custodia técnica.

7. Estado del proyecto

Este documento define el núcleo conceptual del Protocolo AEE. Cualquier implementación debe adherir estrictamente a estos principios.
