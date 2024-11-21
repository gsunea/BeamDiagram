import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Define classes for each segment
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
        self.sup = (L3 - 175) * (10**(-3))  # EC length adjusted by 175 mm

    def Nx(self, s):
        return np.zeros_like(s)
    
    def Ty(self, s):
        return np.full_like(s, 105)
    
    def Mz(self, s):
        return -300 * s + 195 * (175e-3 + s)

class BC:
    def __init__(self):
        self.inf = 0
        self.sup = 175 * (10**(-3))  # Length of BC is exactly 175 mm

    def Nx(self, s):
        return np.zeros_like(s)
    
    def Ty(self, s):
        return np.full_like(s, -195)
    
    def Mz(self, s):
        return 195 * s

# Streamlit UI for input
st.title("Beam Load and Moment Diagrams with Constraints")

# Add sliders for user input
alpha = st.slider("Angle of diagonal part (alpha in degrees)", 0, 90, 65, step=1)

# Apply the second constraint to calculate L2
L2 = 120 / np.sin(np.radians(alpha))

# Now we can have sliders for L1 and L3, but we need to ensure that the constraint L1 + L2*cos(alpha) + L3 <= 500 is fulfilled
L1_L3_max = 500 - L2 * np.cos(np.radians(alpha))

# Ensure the values are integers for L1_L3_max and step
L1_L3_max_int = int(L1_L3_max)  # Cast to integer for the slider

L1 = st.slider(f"Length of horizontal part AD (L1) (max: {L1_L3_max_int} mm)", 50, L1_L3_max_int, 204, step=1)
L3 = st.slider(f"Length of horizontal part EC (L3) (max: {L1_L3_max_int - L1:.2f} mm)", 50, L1_L3_max_int - L1, 234, step=1)

# Display the calculated value of L2
st.write(f"Calculated length of diagonal part DE (L2): {L2:.2f} mm")

# Create instances of each section
ad = AD(L1)
de = DE(L1, L2, alpha)
ec = EC(L3)
bc = BC()

# Generate values for each section
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

# Combine sections for plotting
x_combined = np.concatenate([x_AD, L1 * (10**-3) + y_DE, L1 * (10**-3) + L2 * (10**-3) + s_EC, L1 * (10**-3) + L2 * (10**-3) + L3 * (10**-3) + s_BC])
Nx_combined = np.concatenate([Nx_AD, Nx_DE, Nx_EC, Nx_BC])
Ty_combined = np.concatenate([Ty_AD, Ty_DE, Ty_EC, Ty_BC])
Mz_combined = np.concatenate([Mz_AD, Mz_DE, Mz_EC, Mz_BC])

# Plotting
fig, axs = plt.subplots(3, 1, figsize=(12, 10))

# Calculate section boundaries
section_boundaries = [
    0,  # Start of AD section
    L1 * (10**-3),  # End of AD / Start of DE
    (L1 + L2) * (10**-3),  # End of DE / Start of EC
    (L1 + L2 + L3) * (10**-3),  # End of EC / Start of BC
    (L1 + L2 + L3 + 0.175) * (10**-3)  # End of BC section (0.175 is the BC length)
]

# Section names for labeling
section_names = ['AD', 'DE', 'EC', 'BC']

# Shear Force Diagram
axs[0].plot(x_combined * 1000, Ty_combined, label="Shear Force (T_y)", color="blue")
axs[0].axhline(0, color="black", linewidth=0.8, linestyle="--")
axs[0].set_ylabel("Shear Force (N)")
axs[0].legend()
axs[0].grid()

# Axial Force Diagram
axs[1].plot(x_combined * 1000, Nx_combined, label="Axial Force (N_x)", color="green")
axs[1].axhline(0, color="black", linewidth=0.8, linestyle="--")
axs[1].set_ylabel("Axial Force (N)")
axs[1].legend()
axs[1].grid()

# Bending Moment Diagram
axs[2].plot(x_combined * 1000, Mz_combined, label="Bending Moment (M_z)", color="red")
axs[2].axhline(0, color="black", linewidth=0.8, linestyle="--")
axs[2].set_xlabel("Length of Beam (mm)")
axs[2].set_ylabel("Bending Moment (N·m)")
axs[2].legend()
axs[2].grid()

# Add vertical dotted lines to separate sections
for ax in axs:
    for i, (start, end) in enumerate(zip(section_boundaries[:-1], section_boundaries[1:])):
        # Start of section line
        ax.axvline(x=start * 1000, color='gray', linestyle=':', linewidth=1)
        
        # End of section line
        ax.axvline(x=end * 1000, color='gray', linestyle=':', linewidth=1)
        
        # Calculate label position (middle of the section)
        label_x = ((start + end) / 2) * 1000
        
        # Add section labels with darker color and bold font
        ax.text(label_x, ax.get_ylim()[1], section_names[i], 
                horizontalalignment='center', verticalalignment='top', 
                fontsize=10, color='black', fontweight='bold')

plt.tight_layout()
st.pyplot(fig)