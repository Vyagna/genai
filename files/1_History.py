import streamlit as st

st.set_page_config(page_title="History", page_icon="🗂️", layout="wide")
st.title("History (Session)")

if "records" not in st.session_state or not st.session_state["records"]:
    st.info("No records yet in this session.")
else:
    for rec in reversed(st.session_state["records"]):
        with st.expander(f"#{rec['id']} — {rec['source_type']} — {rec.get('filename') or ''}"):
            st.subheader("Content")
            st.code(rec["content"])
            res = rec["analysis"]
            st.subheader("Analysis")
            st.metric("Risk Score", f"{res['risk_score']:.2f}")
            st.write(f"Risk Label: {res['risk_label']}")
            st.json({"flagged_items": res["flagged_items"]})
            st.download_button(
                "Download JSON report",
                data=str(res["raw"]).encode("utf-8"),
                file_name=f"report_{rec['id']}.json",
                mime="application/json",
                key=f"page_dl_{rec['id']}"
            )
