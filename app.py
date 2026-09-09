import io
import datetime
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="Molway Job Corner - Core Traits Self Assessment",
    layout="wide",
)

# Use relative paths so it works seamlessly on local machine and Streamlit Cloud
LOGO_PATH = "MOLWAY_JOBCorner_Logo1.png"
EXCEL_PATH = "Core Traits Self Assesment_2026.xlsx"

# App Title & Branding
col1, col2 = st.columns([1, 4])
with col1:
  try:
    st.image(LOGO_PATH, width=150)
  except Exception:
    st.warning("Logo not found. Please check the file path.")
with col2:
  st.title("Molway Job Corner")
  st.subheader("Core Traits Self-Assessment & Certification Portal")

st.markdown(
    "Please fill out your personal details and complete the self-assessment"
    " ratings below (1 to 5 scale). Once completed, you can generate and"
    " download your official assessment certificate."
)

# Candidate Information Section
st.markdown("**Candidate Information**")
col_a, col_b, col_c = st.columns(3)
with col_a:
  candidate_name = st.text_input("Full Name", placeholder="Enter your full name")
with col_b:
  candidate_email = st.text_input("Email Address", placeholder="name@example.com")
with col_c:
  assessment_date = st.date_input(
      "Assessment Date", value=datetime.date.today()
  )


# Load Assessment Data from Excel
@st.cache_data
def load_assessment_data():
  df = pd.read_excel(EXCEL_PATH, sheet_name=0)
  df["Trait (English)"] = df["Trait (English)"].ffill()
  df["பண்பு (Tamil)"] = df["பண்பு (Tamil)"].ffill()
  return df


try:
  df_traits = load_assessment_data()
except Exception as e:
  st.error(f"Error loading Excel file: {e}. Please check the file path.")
  st.stop()

st.markdown("---")
st.markdown("**Assessment Questionnaire (Big Five Personality Traits)**")

user_responses = {}
traits = df_traits["Trait (English)"].unique()

for trait in traits:
  trait_df = df_traits[df_traits["Trait (English)"] == trait]
  tamil_trait = trait_df["பண்பு (Tamil)"].iloc[0]

  st.markdown(f"**Trait: {trait} ({tamil_trait})**")

  for idx, row in trait_df.iterrows():
    facet_eng = row["Facet (English)"]
    facet_tam = row["அம்சம் (Tamil)"]

    col_f1, col_f2, col_f3 = st.columns([2, 1, 2])
    with col_f1:
      st.markdown(f"* {facet_eng} / {facet_tam}")
    with col_f2:
      rating = st.slider(
          f"Rating ({idx})",
          min_value=1,
          max_value=5,
          value=3,
          key=f"rating_{idx}",
          label_visibility="collapsed",
      )
    with col_f3:
      comment = st.text_input(
          f"Comment ({idx})",
          placeholder="Optional comment/example",
          key=f"comment_{idx}",
          label_visibility="collapsed",
      )

    user_responses[idx] = {
        "Trait": trait,
        "Tamil_Trait": tamil_trait,
        "Facet": facet_eng,
        "Tamil_Facet": facet_tam,
        "Rating": rating,
        "Comment": comment,
    }
  st.markdown("")


# PDF Generation Function
def generate_pdf(name, email, date_str, responses):
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=letter,
      rightMargin=40,
      leftMargin=40,
      topMargin=40,
      bottomMargin=40,
  )

  styles = getSampleStyleSheet()
  title_style = ParagraphStyle(
      "CertTitle",
      parent=styles["Heading1"],
      fontSize=20,
      textColor=colors.HexColor("#1a365d"),
      alignment=1,
      spaceAfter=10,
  )
  subtitle_style = ParagraphStyle(
      "CertSubtitle",
      parent=styles["Normal"],
      fontSize=12,
      textColor=colors.HexColor("#4a5568"),
      alignment=1,
      spaceAfter=20,
  )
  body_style = ParagraphStyle(
      "CertBody",
      parent=styles["Normal"],
      fontSize=10,
      textColor=colors.HexColor("#2d3748"),
  )

  elements = []

  # Add Logo
  try:
    logo = RLImage(LOGO_PATH, width=120, height=70)
    logo.hAlign = "CENTER"
    elements.append(logo)
    elements.append(Spacer(1, 10))
  except Exception:
    pass

  elements.append(Paragraph("MOLWAY JOB CORNER", title_style))
  elements.append(
      Paragraph(
          "Certificate of Core Traits Self-Assessment", subtitle_style
      )
  )
  elements.append(Spacer(1, 15))

  # Candidate Details Table
  details_data = [
      [
          Paragraph(f"<b>Candidate Name:</b> {name}", body_style),
          Paragraph(f"<b>Date:</b> {date_str}", body_style),
      ],
      [
          Paragraph(f"<b>Email:</b> {email}", body_style),
          Paragraph("<b>Status:</b> Completed", body_style),
      ],
  ]
  t_details = Table(details_data, colWidths=[270, 270])
  t_details.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f7fafc")),
          ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e0")),
          ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
          ("TOPPADDING", (0, 0), (-1, -1), 8),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
          ("LEFTPADDING", (0, 0), (-1, -1), 10),
          ("RIGHTPADDING", (0, 0), (-1, -1), 10),
      ])
  )
  elements.append(t_details)
  elements.append(Spacer(1, 20))

  elements.append(
      Paragraph(
          "<b>Assessment Summary & Ratings</b>",
          ParagraphStyle(
              "Heading2",
              parent=styles["Heading2"],
              fontSize=14,
              textColor=colors.HexColor("#2b6cb0"),
              spaceAfter=10,
          ),
      )
  )

  # Table of ratings
  table_data = [["Trait", "Facet", "Rating", "Comments / Examples"]]
  for idx, resp in responses.items():
    table_data.append([
        Paragraph(resp["Trait"], body_style),
        Paragraph(resp["Facet"], body_style),
        Paragraph(str(resp["Rating"]), body_style),
        Paragraph(resp["Comment"] if resp["Comment"] else "-", body_style),
    ])

  t_ratings = Table(table_data, colWidths=[110, 150, 50, 230])
  t_ratings.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2b6cb0")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
          ("TOPPADDING", (0, 0), (-1, 0), 6),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#f7fafc")],
          ),
          ("TOPPADDING", (0, 1), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
      ])
  )
  elements.append(t_ratings)
  elements.append(Spacer(1, 30))

  # Signature block
  sig_data = [
      [
          Paragraph("<b>Candidate Signature</b>", body_style),
          Paragraph("<b>Verified by Molway Job Corner</b>", body_style),
      ],
      [
          Paragraph("<br/><br/>___________________________", body_style),
          Paragraph("<br/><br/>___________________________", body_style),
      ],
  ]
  t_sig = Table(sig_data, colWidths=[270, 270])
  t_sig.setStyle(
      TableStyle([
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("TOPPADDING", (0, 0), (-1, -1), 2),
      ])
  )
  elements.append(t_sig)

  doc.build(elements)
  buffer.seek(0)
  return buffer


# Submission Button
if st.button("Generate & Download Certificate PDF", type="primary"):
  if not candidate_name.strip():
    st.error("Please enter your candidate name before generating the certificate.")
  else:
    pdf_buffer = generate_pdf(
        candidate_name, candidate_email, str(assessment_date), user_responses
    )
    st.success("Certificate generated successfully!")
    st.download_button(
        label="Download PDF Certificate",
        data=pdf_buffer,
        file_name=(
            f"Molway_Self_Assessment_{candidate_name.replace(' ', '_')}.pdf"
        ),
        mime="application/pdf",
    )
