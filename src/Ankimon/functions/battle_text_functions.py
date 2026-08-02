from aqt import mw

def effectiveness_text(effect_value):
    t = mw.translator.translate
    if effect_value == 0:
        effective_txt = t("eff.missed")
    elif effect_value <= 0.5:
        effective_txt = t("eff.not_very")
    elif effect_value <= 1:
        effective_txt = t("eff.effective")
    elif effect_value <= 1.5:
        effective_txt = t("eff.very")
    elif effect_value <= 2:
        effective_txt = t("eff.super")
    else:
        effective_txt = t("eff.effective")
        #return None
    return effective_txt
