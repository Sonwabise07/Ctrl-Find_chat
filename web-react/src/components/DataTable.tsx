import './DataTable.css';

export interface TableColumn {
  key: string;
  title: string;
}

interface Props {
  columns: TableColumn[];
  rows: Record<string, string>[];
  label: string;
}

export function DataTable({ columns, rows, label }: Props) {
  return (
    <div className="table-wrap">
      <table className="data-table" aria-label={label}>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key} scope="col">
                {column.title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={index}>
              {columns.map((column) => (
                <td key={column.key}>{row[column.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
