def factor(x: float) -> float:
    return x

def product(x: float) -> float:
    return factor(x) * factor(x)

def state(t: float) -> dict:
    if not 0.4 <= t <= 1.6:
        raise ValueError("t outside storyboard interval")
    return {"t": t, "right_factor": factor(t), "left_factor": factor(-t), "right_product": product(t), "left_product": product(-t)}
