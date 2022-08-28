from pathlib import Path


def export_to_csv(df, filename, header=False):
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(filename, header=header, index=False)
