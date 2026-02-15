from src.ingestion import load_data
from src.preprocessing import preprocess
from src.train import train_model
from src.evaluate import evaluate_model


def run_pipeline():
    try:
        print(".......MLOps PipeLine Started.......")

        print("\n[Step 1/4] Ingesting Data...")
        load_data()

        print("\n[Step 2/4] Preprocessing Data...")
        preprocess()

        print("\n[Step 3/4] Training Model...")
        train_model()

        print("\n[Step 4/4] Evaluating Model...")
        evaluate_model()

        print("\n🏆 Pipeline Completed Successfully!")

    except Exception as e:
        print(f"\n❌ Pipeline Failed at some step: {e}")

if __name__ == "__main__":
    run_pipeline()