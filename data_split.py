import marimo

__generated_with = "0.20.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import pandas as pd

    current_dir = os.getcwd()
    print(f"Текущая директория: {current_dir}")
    return (pd,)


@app.cell
def _(pd):
    df = pd.read_csv('../data/raw/flats.csv')
    return (df,)


@app.cell
def _(pd):
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.max_rows', None)     # Show all rows
    return


@app.cell
def _(df):
    df.shape
    return


@app.cell
def _(df):
    df.head(2)
    return


@app.cell
def _(df):
    val_size = int(df.shape[0] * 0.2)
    val_size
    return (val_size,)


@app.cell
def _(df, val_size):
    # Train
    train_df = df[val_size*2:]

    # Validation/Eval
    eval_df = df[val_size:val_size*2]

    # Holdout
    holdout_df = df[:val_size]

    print("Train shape:", train_df.shape)
    print("Eval shape:", eval_df.shape)
    print("Holdout shape:", holdout_df.shape)
    return eval_df, holdout_df, train_df


@app.cell
def _(train_df):
    train_df.head(2)
    return


@app.cell
def _(eval_df):
    eval_df.head(2)
    return


@app.cell
def _(holdout_df):
    holdout_df.head(2)
    return


@app.cell
def _(eval_df, holdout_df, train_df):
    # Save splits
    train_df.to_csv("../data/raw/train.csv", index=False)
    eval_df.to_csv("../data/raw/eval.csv", index=False)
    holdout_df.to_csv("../data/raw/holdout.csv", index=False)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
