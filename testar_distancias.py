import os

pasta = r"C:\Users\Usuario\Desktop\tcc_benchmark\instancias"

for sub in sorted(os.listdir(pasta)):
    if "500" not in sub:
        continue
    vrp_path = os.path.join(pasta, sub)
    for arq in os.listdir(vrp_path):
        if arq.endswith(".vrp") and not arq.endswith(".png"):
            with open(os.path.join(vrp_path, arq)) as f:
                conteudo = f.read()
            vals = []
            modo = False
            for linha in conteudo.split():
                if linha == "EDGE_WEIGHT_SECTION":
                    modo = True
                    continue
                if linha == "DISPLAY_DATA_SECTION":
                    break
                if modo:
                    try:
                        v = float(linha)
                        if v > 0:
                            vals.append(v)
                    except:
                        pass
            print(f"{arq}: min={min(vals):.1f}  max={max(vals):.1f}  media={sum(vals)/len(vals):.1f}")
            break