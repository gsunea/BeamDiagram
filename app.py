import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Definir classes per cada segment
class AD:
    def __init__(self, L1):
        self.inf = 0
        self.sup = L1 * (10**(-3))

    def Nx(self, x):
        return np.zeros_like(x)
    
    def Ty(self, x):
        return np.full_like(x, 105)
    
    def Mz(self, x):
        return 105 * x

class DE:
    def __init__(self, L1, L2, alpha):
        self.inf = 0
        self.L1 = L1 * (10**(-3))
        self.sup = L2 * (10**(-3))
        self.alpha = np.radians(alpha)

    def Nx(self, y):
        return np.full_like(y, 105 * np.sin(self.alpha))
    
    def Ty(self, y):
        return np.full_like(y, 105 * np.cos(self.alpha))
    
    def Mz(self, y):
        return 105 * (self.L1 + y * np.cos(self.alpha))

class EC:
    def __init__(self, L3):
        self.inf = 0
        self.sup = (L3 - 175) * (10**(-3))  # Longitud d'EC ajustada per 175 mm

    def Nx(self, s):
        return np.zeros_like(s)
    
    def Ty(self, s):
        return np.full_like(s, 105)
    
    def Mz(self, s):
        return -300 * s + 195 * (175e-3 + s)

class BC:
    def __init__(self):
        self.inf = 0
        self.sup = 175 * (10**(-3))  # Longitud de BC és exactament 175 mm

    def Nx(self, s):
        return np.zeros_like(s)
    
    def Ty(self, s):
        return np.full_like(s, -195)
    
    def Mz(self, s):
        return 195 * s

# Interfície d'usuari de Streamlit
st.title("Diagrama de Càrregues i Moments de Biga amb Restriccions")

# Afegir controls lliscants per a l'entrada de l'usuari
alpha = st.slider("Angle de la part diagonal (alpha en graus)", 0, 90, 65, step=1)

# Aplicar la segona restricció per calcular L2
L2 = 120 / np.sin(np.radians(alpha))

# Ara podem tenir controls lliscants per a L1 i L3, però cal assegurar que L1 + L2*cos(alpha) + L3 <= 500
L1_L3_max = 500 - L2 * np.cos(np.radians(alpha))

# Assegurar que els valors siguin enters per L1_L3_max i el pas
L1_L3_max_int = int(L1_L3_max)  # Convertir a enter per al control lliscant

L1 = st.slider(f"Longitud de la part horitzontal AD (L1) (màxim: {L1_L3_max_int} mm)", 50, L1_L3_max_int, 204, step=1)
L3 = st.slider(f"Longitud de la part horitzontal EC (L3) (màxim: {L1_L3_max_int - L1:.2f} mm)", 50, L1_L3_max_int - L1, 234, step=1)

# Mostrar el valor calculat de L2
st.write(f"Longitud calculada de la part diagonal DE (L2): {L2:.2f} mm")

# Crear instàncies de cada secció
ad = AD(L1)
de = DE(L1, L2, alpha)
ec = EC(L3)
bc = BC()

# Generar valors per a cada secció
x_AD = np.linspace(ad.inf, ad.sup, 100)
Nx_AD = ad.Nx(x_AD)
Ty_AD = ad.Ty(x_AD)
Mz_AD = ad.Mz(x_AD)

y_DE = np.linspace(de.inf, de.sup, 100)
Nx_DE = de.Nx(y_DE)
Ty_DE = de.Ty(y_DE)
Mz_DE = de.Mz(y_DE)

s_EC = np.linspace(ec.inf, ec.sup, 100)
Nx_EC = ec.Nx(s_EC)
Ty_EC = ec.Ty(s_EC)
Mz_EC = ec.Mz(s_EC)

s_BC = np.linspace(bc.inf, bc.sup, 100)
Nx_BC = bc.Nx(s_BC)
Ty_BC = bc.Ty(s_BC)
Mz_BC = bc.Mz(s_BC)

# Combinar seccions per a la representació gràfica
x_combined = np.concatenate([x_AD, L1 * (10**-3) + y_DE, L1 * (10**-3) + L2 * (10**-3) + s_EC, L1 * (10**-3) + L2 * (10**-3) + L3 * (10**-3) + s_BC])
Nx_combined = np.concatenate([Nx_AD, Nx_DE, Nx_EC, Nx_BC])
Ty_combined = np.concatenate([Ty_AD, Ty_DE, Ty_EC, Ty_BC])
Mz_combined = np.concatenate([Mz_AD, Mz_DE, Mz_EC, Mz_BC])

# Representació gràfica
fig, axs = plt.subplots(3, 1, figsize=(12, 10))

# Calcular límits de les seccions
section_boundaries = [
    0,  # Inici de la secció AD
    L1 * (10**-3),  # Final de AD / Inici de DE
    (L1 + L2) * (10**-3),  # Final de DE / Inici de EC
    (L1 + L2 + L3) * (10**-3),  # Final de EC / Inici de BC
    (L1 + L2 + L3 + 0.175) * (10**-3)  # Final de la secció BC (0.175 és la longitud de BC)
]

# Noms de les seccions per a les etiquetes
section_names = ['AD', 'DE', 'EC', 'BC']

# Diagrama de Força Axial (primera gràfica)
axs[0].plot(x_combined * 1000, Nx_combined, label="Força Axial (N_x)", color="green")
axs[0].axhline(0, color="black", linewidth=0.8, linestyle="--")
axs[0].set_ylabel("Força Axial (N)")
axs[0].legend()
axs[0].grid()

# Diagrama de Força Tallant (segona gràfica)
axs[1].plot(x_combined * 1000, Ty_combined, label="Força Tallant (T_y)", color="blue")
axs[1].axhline(0, color="black", linewidth=0.8, linestyle="--")
axs[1].set_ylabel("Força Tallant (N)")
axs[1].legend()
axs[1].grid()

# Diagrama de Moment Flector (tercera gràfica)
axs[2].plot(x_combined * 1000, Mz_combined, label="Moment Flector (M_z)", color="red")
axs[2].axhline(0, color="black", linewidth=0.8, linestyle="--")
axs[2].set_xlabel("Longitud de la Biga (mm)")
axs[2].set_ylabel("Moment Flector (N·m)")
axs[2].legend()
axs[2].grid()

# Afegir línies verticals discontínues per separar seccions
for ax in axs:
    for i, (start, end) in enumerate(zip(section_boundaries[:-1], section_boundaries[1:])):
        # Línia d'inici de secció
        ax.axvline(x=start * 1000, color='gray', linestyle=':', linewidth=1)
        
        # Línia de final de secció
        ax.axvline(x=end * 1000, color='gray', linestyle=':', linewidth=1)
        
        # Calcular posició de l'etiqueta (al mig de la secció)
        label_x = ((start + end) / 2) * 1000
        
        # Afegir etiquetes de seccions amb un color més fosc i lletra en negreta
        ax.text(label_x, ax.get_ylim()[1], section_names[i], 
                horizontalalignment='center', verticalalignment='top', 
                fontsize=10, color='black', fontweight='bold')

plt.tight_layout()
st.pyplot(fig)