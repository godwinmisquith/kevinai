"""Data analyst tool for data analysis, visualization, and SQL operations."""

import base64
import io
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.tools.base import BaseTool


class DataAnalystTool(BaseTool):
    """Tool for data analysis, visualization, and SQL operations."""

    name = "data_analyst"
    description = "Analyze data, create visualizations, and run SQL queries"

    def __init__(self):
        self.temp_db_path: Optional[str] = None
        self._ensure_dependencies()

    def _ensure_dependencies(self) -> None:
        """Check if required dependencies are available."""
        self.pandas_available = False
        self.matplotlib_available = False
        self.openpyxl_available = False

        try:
            import pandas  # noqa: F401
            self.pandas_available = True
        except ImportError:
            pass

        try:
            import matplotlib
            matplotlib.use('Agg')
            self.matplotlib_available = True
        except ImportError:
            pass

        try:
            import openpyxl  # noqa: F401
            self.openpyxl_available = True
        except ImportError:
            pass

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a data analyst operation."""
        operations = {
            "read_csv": self.read_csv,
            "read_excel": self.read_excel,
            "read_json": self.read_json_data,
            "analyze": self.analyze_data,
            "describe": self.describe_data,
            "filter": self.filter_data,
            "aggregate": self.aggregate_data,
            "visualize": self.create_visualization,
            "sql_query": self.sql_query,
            "sql_create_table": self.sql_create_table,
            "export_csv": self.export_csv,
            "export_excel": self.export_excel,
            "correlation": self.correlation_analysis,
            "pivot": self.pivot_table,
            "merge": self.merge_datasets,
            "clean": self.clean_data,
            "transform": self.transform_data,
            "statistics": self.statistical_analysis,
        }

        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}

        return await operations[operation](**kwargs)

    async def read_csv(
        self,
        file_path: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Read a CSV file into a dataframe."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
            return {
                "success": True,
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "preview": df.head(10).to_dict(orient="records"),
                "shape": list(df.shape),
            }
        except Exception as e:
            return {"error": str(e)}

    async def read_excel(
        self,
        file_path: str,
        sheet_name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Read an Excel file into a dataframe."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}
        if not self.openpyxl_available:
            return {"error": "openpyxl is not installed. Run: pip install openpyxl"}

        try:
            import pandas as pd

            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)

            return {
                "success": True,
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "preview": df.head(10).to_dict(orient="records"),
                "shape": list(df.shape),
            }
        except Exception as e:
            return {"error": str(e)}

    async def read_json_data(
        self,
        file_path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Read a JSON file into a dataframe."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            df = pd.read_json(file_path)
            return {
                "success": True,
                "rows": len(df),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "preview": df.head(10).to_dict(orient="records"),
                "shape": list(df.shape),
            }
        except Exception as e:
            return {"error": str(e)}

    async def analyze_data(
        self,
        file_path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform comprehensive data analysis on a file."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            # Detect file type and read
            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            elif ext == ".json":
                df = pd.read_json(file_path)
            else:
                return {"error": f"Unsupported file type: {ext}"}

            # Basic info
            analysis = {
                "success": True,
                "shape": list(df.shape),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing_values": df.isnull().sum().to_dict(),
                "missing_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            }

            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if numeric_cols:
                analysis["numeric_summary"] = df[numeric_cols].describe().to_dict()

            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            if categorical_cols:
                analysis["categorical_summary"] = {
                    col: {
                        "unique_values": df[col].nunique(),
                        "top_values": df[col].value_counts().head(5).to_dict(),
                    }
                    for col in categorical_cols[:5]  # Limit to first 5 categorical columns
                }

            # Memory usage
            analysis["memory_usage_mb"] = round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)

            return analysis
        except Exception as e:
            return {"error": str(e)}

    async def describe_data(
        self,
        file_path: str,
        columns: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get descriptive statistics for data."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            if columns:
                df = df[columns]

            description = df.describe(include="all").to_dict()
            return {
                "success": True,
                "description": description,
            }
        except Exception as e:
            return {"error": str(e)}

    async def filter_data(
        self,
        file_path: str,
        condition: str,
        output_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Filter data based on a condition."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            # Apply filter using query
            filtered_df = df.query(condition)

            result = {
                "success": True,
                "original_rows": len(df),
                "filtered_rows": len(filtered_df),
                "preview": filtered_df.head(10).to_dict(orient="records"),
            }

            if output_path:
                if output_path.endswith(".csv"):
                    filtered_df.to_csv(output_path, index=False)
                elif output_path.endswith(".xlsx"):
                    filtered_df.to_excel(output_path, index=False)
                result["output_path"] = output_path

            return result
        except Exception as e:
            return {"error": str(e)}

    async def aggregate_data(
        self,
        file_path: str,
        group_by: List[str],
        aggregations: Dict[str, str],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Aggregate data by grouping."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            # Perform aggregation
            agg_result = df.groupby(group_by).agg(aggregations).reset_index()

            return {
                "success": True,
                "rows": len(agg_result),
                "columns": list(agg_result.columns),
                "result": agg_result.to_dict(orient="records"),
            }
        except Exception as e:
            return {"error": str(e)}

    async def create_visualization(
        self,
        file_path: str,
        chart_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        title: Optional[str] = None,
        output_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a data visualization."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}
        if not self.matplotlib_available:
            return {"error": "matplotlib is not installed. Run: pip install matplotlib"}

        try:
            import pandas as pd
            import matplotlib.pyplot as plt

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "bar":
                if x_column and y_column:
                    df.plot(kind="bar", x=x_column, y=y_column, ax=ax)
                else:
                    df.plot(kind="bar", ax=ax)
            elif chart_type == "line":
                if x_column and y_column:
                    df.plot(kind="line", x=x_column, y=y_column, ax=ax)
                else:
                    df.plot(kind="line", ax=ax)
            elif chart_type == "scatter":
                if x_column and y_column:
                    df.plot(kind="scatter", x=x_column, y=y_column, ax=ax)
                else:
                    return {"error": "scatter plot requires x_column and y_column"}
            elif chart_type == "histogram":
                if y_column:
                    df[y_column].plot(kind="hist", ax=ax, bins=30)
                else:
                    df.plot(kind="hist", ax=ax, bins=30)
            elif chart_type == "pie":
                if y_column:
                    df[y_column].value_counts().plot(kind="pie", ax=ax, autopct='%1.1f%%')
                else:
                    return {"error": "pie chart requires y_column"}
            elif chart_type == "box":
                if y_column:
                    df.boxplot(column=y_column, ax=ax)
                else:
                    df.boxplot(ax=ax)
            elif chart_type == "heatmap":
                numeric_df = df.select_dtypes(include=["number"])
                corr = numeric_df.corr()
                im = ax.imshow(corr, cmap="coolwarm", aspect="auto")
                ax.set_xticks(range(len(corr.columns)))
                ax.set_yticks(range(len(corr.columns)))
                ax.set_xticklabels(corr.columns, rotation=45, ha="right")
                ax.set_yticklabels(corr.columns)
                plt.colorbar(im, ax=ax)
            else:
                return {"error": f"Unknown chart type: {chart_type}"}

            if title:
                ax.set_title(title)

            plt.tight_layout()

            # Save or return as base64
            if output_path:
                plt.savefig(output_path, dpi=150, bbox_inches="tight")
                plt.close()
                return {
                    "success": True,
                    "output_path": output_path,
                    "chart_type": chart_type,
                }
            else:
                buf = io.BytesIO()
                plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
                buf.seek(0)
                image_base64 = base64.b64encode(buf.read()).decode("utf-8")
                plt.close()
                return {
                    "success": True,
                    "chart_type": chart_type,
                    "image": image_base64,
                    "format": "base64_png",
                }
        except Exception as e:
            return {"error": str(e)}

    async def sql_query(
        self,
        query: str,
        file_path: Optional[str] = None,
        table_name: str = "data",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a SQL query on data."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            # Create or use temp database
            if not self.temp_db_path:
                self.temp_db_path = tempfile.mktemp(suffix=".db")

            conn = sqlite3.connect(self.temp_db_path)

            # If file_path provided, load data into table
            if file_path:
                ext = Path(file_path).suffix.lower()
                if ext == ".csv":
                    df = pd.read_csv(file_path)
                elif ext in [".xlsx", ".xls"]:
                    df = pd.read_excel(file_path)
                else:
                    df = pd.read_json(file_path)

                df.to_sql(table_name, conn, if_exists="replace", index=False)

            # Execute query
            result_df = pd.read_sql_query(query, conn)
            conn.close()

            return {
                "success": True,
                "rows": len(result_df),
                "columns": list(result_df.columns),
                "result": result_df.to_dict(orient="records"),
            }
        except Exception as e:
            return {"error": str(e)}

    async def sql_create_table(
        self,
        file_path: str,
        table_name: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a SQL table from a data file."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            if not self.temp_db_path:
                self.temp_db_path = tempfile.mktemp(suffix=".db")

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            conn = sqlite3.connect(self.temp_db_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.close()

            return {
                "success": True,
                "table_name": table_name,
                "rows": len(df),
                "columns": list(df.columns),
            }
        except Exception as e:
            return {"error": str(e)}

    async def export_csv(
        self,
        data: List[Dict[str, Any]],
        output_path: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Export data to CSV."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            return {
                "success": True,
                "output_path": output_path,
                "rows": len(df),
            }
        except Exception as e:
            return {"error": str(e)}

    async def export_excel(
        self,
        data: List[Dict[str, Any]],
        output_path: str,
        sheet_name: str = "Sheet1",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Export data to Excel."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}
        if not self.openpyxl_available:
            return {"error": "openpyxl is not installed. Run: pip install openpyxl"}

        try:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_excel(output_path, sheet_name=sheet_name, index=False)
            return {
                "success": True,
                "output_path": output_path,
                "rows": len(df),
            }
        except Exception as e:
            return {"error": str(e)}

    async def correlation_analysis(
        self,
        file_path: str,
        columns: Optional[List[str]] = None,
        method: str = "pearson",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Calculate correlation between numeric columns."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            if columns:
                df = df[columns]

            numeric_df = df.select_dtypes(include=["number"])
            corr = numeric_df.corr(method=method)

            return {
                "success": True,
                "method": method,
                "correlation_matrix": corr.to_dict(),
            }
        except Exception as e:
            return {"error": str(e)}

    async def pivot_table(
        self,
        file_path: str,
        index: List[str],
        columns: Optional[List[str]] = None,
        values: Optional[List[str]] = None,
        aggfunc: str = "mean",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a pivot table."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            pivot = pd.pivot_table(
                df,
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
            )

            return {
                "success": True,
                "shape": list(pivot.shape),
                "result": pivot.reset_index().to_dict(orient="records"),
            }
        except Exception as e:
            return {"error": str(e)}

    async def merge_datasets(
        self,
        file_path_1: str,
        file_path_2: str,
        on: Optional[List[str]] = None,
        how: str = "inner",
        output_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Merge two datasets."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            # Read first file
            ext1 = Path(file_path_1).suffix.lower()
            if ext1 == ".csv":
                df1 = pd.read_csv(file_path_1)
            elif ext1 in [".xlsx", ".xls"]:
                df1 = pd.read_excel(file_path_1)
            else:
                df1 = pd.read_json(file_path_1)

            # Read second file
            ext2 = Path(file_path_2).suffix.lower()
            if ext2 == ".csv":
                df2 = pd.read_csv(file_path_2)
            elif ext2 in [".xlsx", ".xls"]:
                df2 = pd.read_excel(file_path_2)
            else:
                df2 = pd.read_json(file_path_2)

            # Merge
            merged = pd.merge(df1, df2, on=on, how=how)

            result = {
                "success": True,
                "rows": len(merged),
                "columns": list(merged.columns),
                "preview": merged.head(10).to_dict(orient="records"),
            }

            if output_path:
                if output_path.endswith(".csv"):
                    merged.to_csv(output_path, index=False)
                elif output_path.endswith(".xlsx"):
                    merged.to_excel(output_path, index=False)
                result["output_path"] = output_path

            return result
        except Exception as e:
            return {"error": str(e)}

    async def clean_data(
        self,
        file_path: str,
        operations: List[str],
        output_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Clean data with various operations."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            original_shape = df.shape
            applied_operations = []

            for op in operations:
                if op == "drop_duplicates":
                    df = df.drop_duplicates()
                    applied_operations.append("drop_duplicates")
                elif op == "drop_na":
                    df = df.dropna()
                    applied_operations.append("drop_na")
                elif op == "fill_na_zero":
                    df = df.fillna(0)
                    applied_operations.append("fill_na_zero")
                elif op == "fill_na_mean":
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    applied_operations.append("fill_na_mean")
                elif op == "strip_whitespace":
                    string_cols = df.select_dtypes(include=["object"]).columns
                    df[string_cols] = df[string_cols].apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                    applied_operations.append("strip_whitespace")
                elif op == "lowercase":
                    string_cols = df.select_dtypes(include=["object"]).columns
                    df[string_cols] = df[string_cols].apply(lambda x: x.str.lower() if x.dtype == "object" else x)
                    applied_operations.append("lowercase")

            result = {
                "success": True,
                "original_shape": list(original_shape),
                "new_shape": list(df.shape),
                "applied_operations": applied_operations,
                "preview": df.head(10).to_dict(orient="records"),
            }

            if output_path:
                if output_path.endswith(".csv"):
                    df.to_csv(output_path, index=False)
                elif output_path.endswith(".xlsx"):
                    df.to_excel(output_path, index=False)
                result["output_path"] = output_path

            return result
        except Exception as e:
            return {"error": str(e)}

    async def transform_data(
        self,
        file_path: str,
        transformations: Dict[str, str],
        output_path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transform data columns."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            # Apply transformations
            for new_col, expression in transformations.items():
                df[new_col] = df.eval(expression)

            result = {
                "success": True,
                "columns": list(df.columns),
                "preview": df.head(10).to_dict(orient="records"),
            }

            if output_path:
                if output_path.endswith(".csv"):
                    df.to_csv(output_path, index=False)
                elif output_path.endswith(".xlsx"):
                    df.to_excel(output_path, index=False)
                result["output_path"] = output_path

            return result
        except Exception as e:
            return {"error": str(e)}

    async def statistical_analysis(
        self,
        file_path: str,
        column: str,
        tests: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform statistical analysis on a column."""
        if not self.pandas_available:
            return {"error": "pandas is not installed. Run: pip install pandas"}

        try:
            import pandas as pd

            ext = Path(file_path).suffix.lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                df = pd.read_json(file_path)

            data = df[column].dropna()

            stats = {
                "success": True,
                "column": column,
                "count": len(data),
                "mean": float(data.mean()),
                "median": float(data.median()),
                "std": float(data.std()),
                "var": float(data.var()),
                "min": float(data.min()),
                "max": float(data.max()),
                "range": float(data.max() - data.min()),
                "skewness": float(data.skew()),
                "kurtosis": float(data.kurtosis()),
                "percentiles": {
                    "25%": float(data.quantile(0.25)),
                    "50%": float(data.quantile(0.50)),
                    "75%": float(data.quantile(0.75)),
                    "90%": float(data.quantile(0.90)),
                    "95%": float(data.quantile(0.95)),
                    "99%": float(data.quantile(0.99)),
                },
            }

            return stats
        except Exception as e:
            return {"error": str(e)}
