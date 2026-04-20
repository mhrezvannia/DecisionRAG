APP_CSS = """
<style>
    :root {
        --bg: #08111f;
        --bg-soft: #0d1728;
        --panel: #101c30;
        --panel-alt: #13223a;
        --panel-hover: #162845;
        --line: #21324f;
        --line-soft: #1b2940;
        --text: #edf4ff;
        --muted: #96a9c5;
        --accent: #65a8ff;
        --accent-strong: #8bc0ff;
        --accent-soft: rgba(101, 168, 255, 0.12);
        --success: #7fe2af;
        --warning: #f3c279;
        --neutral: #c0cde0;
        --shadow: 0 24px 50px rgba(2, 8, 18, 0.42);
    }

    html, body, [class*="css"] {
        font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(41, 76, 125, 0.45), transparent 26%),
            radial-gradient(circle at top right, rgba(24, 44, 77, 0.35), transparent 22%),
            linear-gradient(180deg, #07111f 0%, #0b1628 100%);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(8, 17, 31, 0.68);
        border-bottom: 1px solid rgba(32, 48, 75, 0.85);
        backdrop-filter: blur(14px);
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2.35rem;
        padding-bottom: 2.4rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081321 0%, #0c1627 100%);
        border-right: 1px solid rgba(28, 42, 66, 0.95);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stCaption {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        background: #0e1a2c !important;
    }

    h1, h2, h3, h4 {
        color: var(--text);
        letter-spacing: -0.02em;
    }

    p, label, .stCaption, .stMarkdown, div {
        color: inherit;
    }

    .dr-hero {
        background:
            linear-gradient(135deg, rgba(19, 34, 58, 0.96), rgba(11, 21, 39, 0.96)),
            linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.01));
        border: 1px solid rgba(47, 72, 108, 0.9);
        border-radius: 28px;
        box-shadow: var(--shadow);
        padding: 1.55rem 1.55rem 1.4rem 1.55rem;
        margin-bottom: 1rem;
    }

    .dr-hero-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.9fr);
        gap: 1rem;
        align-items: start;
    }

    .dr-hero-panel,
    .dr-status-tile,
    .dr-evidence-card,
    .dr-inline-note {
        background: rgba(12, 22, 38, 0.72);
        border: 1px solid rgba(38, 58, 89, 0.92);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }

    .dr-hero-panel {
        border-radius: 22px;
        padding: 1rem;
    }

    .dr-kicker {
        color: var(--accent-strong);
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-size: 0.72rem;
        font-weight: 700;
        margin-bottom: 0.45rem;
    }

    .dr-title {
        font-size: 2.55rem;
        line-height: 1.02;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.3rem;
    }

    .dr-subtitle {
        color: #d2def0;
        font-size: 1.08rem;
        margin-bottom: 0.7rem;
    }

    .dr-body {
        color: var(--muted);
        font-size: 0.95rem;
        line-height: 1.7;
    }

    .dr-mini-label {
        color: var(--accent-strong);
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .dr-flow-stack {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
    }

    .dr-chip {
        display: inline-flex;
        align-items: center;
        background: var(--accent-soft);
        color: #ddebff;
        border: 1px solid rgba(98, 143, 208, 0.48);
        border-radius: 999px;
        padding: 0.34rem 0.62rem;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .dr-flow-arrow {
        color: #6e88ab;
        font-size: 0.95rem;
        font-weight: 700;
    }

    .dr-status-tile {
        border-radius: 20px;
        padding: 0.95rem;
        min-height: 138px;
        margin-bottom: 0.9rem;
    }

    .dr-status-value {
        color: var(--text);
        font-size: 1.22rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        line-height: 1.25;
    }

    .dr-status-subvalue {
        color: #c8d6ea;
        font-size: 0.88rem;
        font-weight: 600;
        margin-bottom: 0.55rem;
    }

    .dr-status-body {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .dr-section-intro {
        margin-bottom: 0.7rem;
    }

    .dr-section-title {
        color: var(--text);
        font-size: 1.45rem;
        font-weight: 700;
        margin-bottom: 0.28rem;
    }

    .dr-query-shell,
    .dr-result-shell,
    .dr-evidence-shell,
    .dr-corpus-shell {
        background: rgba(10, 19, 33, 0.75);
        border: 1px solid rgba(36, 55, 85, 0.92);
        border-radius: 24px;
        padding: 1.05rem 1.05rem 0.85rem 1.05rem;
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
    }

    .decision-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        font-size: 0.79rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        margin-bottom: 0.8rem;
    }

    .decision-answer {
        background: rgba(127, 226, 175, 0.12);
        color: var(--success);
        border: 1px solid rgba(127, 226, 175, 0.34);
    }

    .decision-clarify {
        background: rgba(101, 168, 255, 0.13);
        color: var(--accent-strong);
        border: 1px solid rgba(101, 168, 255, 0.32);
    }

    .decision-abstain {
        background: rgba(192, 205, 224, 0.10);
        color: #d0dae8;
        border: 1px solid rgba(165, 181, 207, 0.22);
    }

    .dr-result-copy {
        color: var(--text);
        font-size: 1rem;
        line-height: 1.8;
        margin-bottom: 0.8rem;
    }

    .dr-result-note {
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.7;
    }

    .dr-inline-note {
        border-radius: 16px;
        padding: 0.8rem 0.9rem;
        margin-top: 0.7rem;
        color: #d6e3f6;
        font-size: 0.88rem;
        line-height: 1.6;
    }

    .dr-evidence-card {
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin-top: 0.8rem;
    }

    .dr-evidence-head {
        margin-bottom: 0.72rem;
    }

    .dr-evidence-text {
        color: #e4edf9;
        font-size: 0.93rem;
        line-height: 1.72;
        white-space: pre-wrap;
    }

    .source-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.24rem 0.56rem;
        border-radius: 999px;
        background: rgba(101, 168, 255, 0.11);
        color: #dcebff;
        border: 1px solid rgba(95, 143, 212, 0.32);
        font-size: 0.75rem;
        margin-right: 0.32rem;
        margin-bottom: 0.32rem;
        font-weight: 600;
    }

    .stButton > button {
        background: linear-gradient(180deg, #5b9dff 0%, #3d77cf 100%);
        color: #f8fbff;
        border: 1px solid #5e95ea;
        border-radius: 14px;
        min-height: 2.85rem;
        font-weight: 700;
        box-shadow: 0 12px 24px rgba(61, 119, 207, 0.24);
        transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        background: linear-gradient(180deg, #69a7ff 0%, #4a84dc 100%);
        color: #ffffff;
        box-shadow: 0 16px 30px rgba(61, 119, 207, 0.28);
    }

    .stButton > button:focus {
        box-shadow: 0 0 0 0.18rem rgba(101, 168, 255, 0.22);
    }

    .stTextInput > div > div > input,
    .stTextArea textarea,
    [data-baseweb="input"] input,
    [data-baseweb="base-input"] textarea,
    .stSelectbox div[data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(13, 23, 40, 0.96) !important;
        color: var(--text) !important;
        border: 1px solid rgba(39, 58, 89, 0.96) !important;
        border-radius: 16px !important;
    }

    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stFileUploader > label,
    .stCheckbox > label,
    .stSlider > label {
        color: var(--text) !important;
        font-weight: 600;
    }

    [data-testid="stFileUploaderDropzone"] {
        min-height: 128px;
        padding: 1.05rem !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }

    [data-testid="stFileUploaderDropzone"] section small,
    [data-testid="stFileUploaderDropzone"] section span,
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: var(--muted) !important;
    }

    .stSlider [role="slider"] {
        background: var(--accent);
        box-shadow: none;
        border: 2px solid #d6e8ff;
    }

    .stSlider div[data-testid="stTickBar"] div {
        background: rgba(93, 118, 156, 0.38);
    }

    .stCheckbox label,
    .stRadio label {
        color: var(--text) !important;
    }

    .stMetric {
        background: rgba(14, 25, 43, 0.92);
        border: 1px solid rgba(36, 55, 85, 0.96);
        border-radius: 18px;
        padding: 0.9rem 1rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(10, 19, 33, 0.74);
        border: 1px solid rgba(36, 55, 85, 0.92);
        border-radius: 24px;
        padding: 0.2rem 0.2rem 0.1rem 0.2rem;
        box-shadow: var(--shadow);
    }

    [data-testid="stVerticalBlockBorderWrapper"] > div {
        background: transparent;
    }

    .stTextArea textarea {
        min-height: 120px;
        line-height: 1.7;
        font-size: 1rem;
    }

    .stFileUploader {
        margin-bottom: 0.7rem;
    }

    .stDivider {
        margin-top: 1.2rem;
        margin-bottom: 1.2rem;
    }

    .stMetric label {
        color: var(--muted) !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        color: var(--text);
    }

    .stDataFrame {
        border: 1px solid rgba(36, 55, 85, 0.96);
        border-radius: 18px;
        overflow: hidden;
        background: rgba(10, 19, 33, 0.9);
    }

    [data-testid="stExpander"] {
        border: 1px solid rgba(36, 55, 85, 0.96);
        border-radius: 18px;
        background: rgba(13, 24, 42, 0.84);
    }

    .stAlert {
        border-radius: 16px;
    }

    .stSuccess, .stInfo, .stWarning, .stError {
        background: rgba(12, 22, 38, 0.78);
    }

    .stCaption {
        color: var(--muted) !important;
    }

    @media (max-width: 920px) {
        .dr-hero-grid {
            grid-template-columns: 1fr;
        }

        .dr-title {
            font-size: 2rem;
        }
    }
</style>
"""
