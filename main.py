from src.ingestion import load_data
from src.preprocessing import preprocess
from src.train import train_model
from src.evaluate import evaluate_model


def run_pipeline():
    print(".......MLOps PipeLine Started.......")

    print("\n[Step 1/4] Ingesting Data...")
    load_data()

    print("\n[Step2/4] Preprocessing Data.....")
    preprocess()

    print("\n[Step3/4] Training Model.........")
    train_model()

    print("\n[Step4/4] Evaluating Model.....")
    evaluate_model()

if __name__ == "__main__":
    run_pipeline()