"""
Script to generate PNG images from Mermaid diagrams using mermaid.ink API
Run: python scripts/generate_diagram_images.py
"""
import base64
import requests
from pathlib import Path

# Create images directory
images_dir = Path("images/diagrams")
images_dir.mkdir(parents=True, exist_ok=True)

# Mermaid diagram codes
diagrams = {
    "pipeline": """
flowchart TD
    A[Data Input<br/>762 devices FIELD-only] --> B[SimpleImputer median]
    B --> C[Stratified Split<br/>70/30: 533 train, 229 test]
    C --> D[SMOTE 0.5<br/>Balanced ~250/class]
    D --> E[CatBoost<br/>100 iterations, depth 6, lr 0.1]
    E --> F[Predictions]
    F --> G[Metrics<br/>Recall 57.1%, Precision 57.1%, AUC 0.9186]
    G --> H[Model v2.0<br/>MVP/POC Validated]
""",
    
    "discovery0": """
flowchart TD
    A[False Positive Alert<br/>Device 861275072515287<br/>Score 99.8%] --> B[Investigation<br/>Analyze Raw Payloads]
    B --> C[Pattern Discovery<br/>460 messages analyzed]
    C --> D[⚠️ CONTAMINATION FOUND<br/>179 FACTORY + 281 FIELD<br/>39% factory messages]
    D --> E[Hypothesis Formation<br/>Dataset-wide contamination?]
    E --> F[Dataset-wide Validation<br/>1,141,156 messages analyzed]
    F --> G[✅ CONFIRMED<br/>362,343 FACTORY messages<br/>31.8% total contamination<br/>27 devices affected]
    G --> H{Strategic Decision<br/>Keep v1 78.6% OR<br/>Rebuild FIELD-only?}
    H -->|Option A ❌| I[Keep v1 78.6%<br/>Inflated metrics<br/>Unreliable predictions]
    H -->|Option B ✅| J[Rebuild with<br/>FIELD-only data<br/>762 devices]
    J --> K[Filter Applied<br/>Remove FACTORY messages]
    K --> L[Retrain CatBoost<br/>v2.0 Development]
    L --> M[Result<br/>Recall 57.1% -21.5%<br/>ROC-AUC 0.9186 +6.6%<br/>Clean foundation ✅]
    M --> N[💡 Lesson Learned<br/>Data Quality > Model Complexity<br/>Critical Thinking > Perfect Metrics]
    
    style A fill:#ffcdd2
    style D fill:#fff9c4
    style G fill:#c8e6c9
    style H fill:#ffccbc
    style I fill:#ffcdd2
    style J fill:#c8e6c9
    style M fill:#e1f5fe
    style N fill:#f3e5f5
""",
    
    "research_journey": """
flowchart LR
    Start([🔬 HYPOTHESIS<br/>Can ML predict<br/>IoT failures?]) --> v1{PHASE 2<br/>v1 Development<br/>789 devices}
    
    v1 -->|Recall: 78.6%<br/>Looks great!| discovery([⚠️ PHASE 3<br/>DISCOVERY 0<br/>False Positive<br/>Investigation])
    
    discovery -->|31.8% FACTORY<br/>contamination| pivot{PHASE 4<br/>STRATEGIC PIVOT<br/>Critical Decision}
    
    pivot -->|❌ Option A| keep[Keep v1 78.6%<br/>Inflated metrics]
    pivot -->|✅ Option B| rebuild[Rebuild FIELD-only<br/>Clean data]
    
    keep --> reject[❌ REJECTED<br/>Integrity<br/>compromised]
    
    rebuild --> v2([PHASE 5<br/>v2.0 VALIDATION<br/>762 FIELD-only])
    
    v2 -->|Recall: 57.1% -21.5%<br/>ROC-AUC: 0.9186 +6.6%<br/>Honest baseline ✅| enhance{PHASE 6<br/>v2.1 ENHANCEMENT<br/>Temporal features}
    
    enhance -->|+3 features<br/>Recall +0.1%| decision{Improvement<br/>>= 5% ?}
    
    decision -->|No: +0.1%| mvp([PHASE 7<br/>MVP POSITIONING<br/>v2.0 Honest 57.1%])
    decision -->|Yes| use_v21[Use v2.1]
    
    mvp --> lessons[💡 LESSONS LEARNED<br/>✅ Critical Thinking<br/>✅ Data Quality > Metrics<br/>✅ Resilience<br/>✅ Scientific Rigor<br/>✅ Transparency]
    
    style Start fill:#e3f2fd
    style discovery fill:#fff9c4
    style pivot fill:#ffccbc
    style rebuild fill:#c8e6c9
    style v2 fill:#e1f5fe
    style mvp fill:#c8e6c9
    style lessons fill:#f3e5f5
    style keep fill:#ffcdd2
    style reject fill:#ffcdd2
""",
    
    "fase3_roadmap": """
flowchart TD
    Start([🎯 FASE 3 ROADMAP<br/>From 57.1% MVP to 85%+ Production])
    
    Start --> track1[🕒 Track 1: TEMPORAL FEATURES]
    Start --> track2[⚙️ Track 2: HYPERPARAMETER TUNING]
    Start --> track3[📊 Track 3: DATASET EXPANSION]
    Start --> track4[✅ Track 4: TEMPORAL VALIDATION]
    
    track1 --> t1_1[deployment_age<br/>Time since activation]
    track1 --> t1_2[activity_trends<br/>7-day avg degradation]
    track1 --> t1_3[degradation_delta<br/>Change rate analysis]
    
    t1_1 --> t1_result[💡 Projected: +20% recall<br/>Focus: Early vs late stage failure]
    t1_2 --> t1_result
    t1_3 --> t1_result
    
    track2 --> t2_1[GridSearchCV<br/>depth: 4-10, iterations: 50-200]
    track2 --> t2_2[learning_rate<br/>Test: 0.03, 0.05, 0.1, 0.15]
    track2 --> t2_3[l2_leaf_reg<br/>Regularization tuning]
    
    t2_1 --> t2_result[💡 Projected: +10-15% recall<br/>Focus: Overfitting prevention]
    t2_2 --> t2_result
    t2_3 --> t2_result
    
    track3 --> t3_1[Critical Devices<br/>Sample 100+ FAILED devices]
    track3 --> t3_2[Balanced Dataset<br/>Match OPERATIONAL count]
    track3 --> t3_3[Statistical Power<br/>Achieve 95% confidence]
    
    t3_1 --> t3_result[💡 Impact: Reduce variance<br/>Focus: Generalization]
    t3_2 --> t3_result
    t3_3 --> t3_result
    
    track4 --> t4_1[Time-based Split<br/>Train: < 2025-01-01]
    track4 --> t4_2[Future Testing<br/>Test: >= 2025-01-01]
    track4 --> t4_3[Degradation Check<br/>Monitor drift]
    
    t4_1 --> t4_result[💡 Impact: Real-world validation<br/>Focus: Deployment readiness]
    t4_2 --> t4_result
    t4_3 --> t4_result
    
    t1_result --> combine{COMBINED<br/>IMPROVEMENTS}
    t2_result --> combine
    t3_result --> combine
    t4_result --> combine
    
    combine --> target([🎯 TARGET METRICS<br/>Recall >= 85%<br/>Precision >= 80%<br/>Clean FIELD-only data])
    
    target --> production[✅ PRODUCTION READY<br/>With human oversight<br/>5-10% false alarms acceptable]
    
    style Start fill:#e1f5fe
    style track1 fill:#fff9c4
    style track2 fill:#ffe0b2
    style track3 fill:#f3e5f5
    style track4 fill:#c8e6c9
    style t1_result fill:#fff59d
    style t2_result fill:#ffcc80
    style t3_result fill:#e1bee7
    style t4_result fill:#a5d6a7
    style combine fill:#ffccbc
    style target fill:#c8e6c9
    style production fill:#81c784
"""
}

def generate_image(name, mermaid_code):
    """Generate PNG image from Mermaid code using mermaid.ink API"""
    # Encode Mermaid code to base64
    encoded = base64.urlsafe_b64encode(mermaid_code.strip().encode('utf-8')).decode('ascii')
    
    # mermaid.ink API URL
    url = f"https://mermaid.ink/img/{encoded}"
    
    # Download image
    output_path = images_dir / f"{name}.png"
    
    try:
        print(f"Downloading {name}...")
        response = requests.get(url, verify=False, timeout=30)  # Disable SSL verification for corporate proxy
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Saved: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error downloading {name}: {e}")
        return False

if __name__ == "__main__":
    print("Generating Mermaid diagram images...\n")
    
    success_count = 0
    for name, code in diagrams.items():
        if generate_image(name, code):
            success_count += 1
    
    print(f"\n✅ Successfully generated {success_count}/{len(diagrams)} images")
    print(f"📁 Images saved to: {images_dir.absolute()}")
