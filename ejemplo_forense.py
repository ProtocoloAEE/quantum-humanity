from aee.core import EvidenceProtocol
import json
p = EvidenceProtocol('franco@test.com')
p.initialize()
cert = p.certify_file('prueba.txt')
print(json.dumps(cert, indent=4))
