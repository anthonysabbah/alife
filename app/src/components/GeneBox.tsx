import { GlobalContext, defaultContext } from './GlobalContext';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Legend,
  Title,
  ChartData
} from 'chart.js';
import { Tooltip as TTip} from 'chart.js';
import { Line } from 'react-chartjs-2';
// import "chartjs-plugin-streaming";
import { useState, useEffect, useRef } from 'react';
import useWebSocket from 'react-use-websocket';
import { useContext } from 'react';

import * as React from 'react';
import { alpha } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
// import Checkbox from '@mui/material/Checkbox';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import DeleteIcon from '@mui/icons-material/Delete';
import FilterListIcon from '@mui/icons-material/FilterList';
import { visuallyHidden } from '@mui/utils';
import { Button } from '@mui/material';
import ReplayIcon from '@mui/icons-material/Replay';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  TTip,
  Legend
);

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    // title: {
    //   display: true,
    //   text: 'Chart.js Line Chart',
    // },
  },
};

interface GeneInfo {
  hash: string;
  fitness: number;
}

function createGeneInfo(
  hash: string,
  fitness: number,
): GeneInfo {
  return {
    hash,
    fitness,
  };
}

const defaultRows = [
  createGeneInfo('ghjtyughbv', 69),
  createGeneInfo('sagrsfdgw4tg', 349),
  createGeneInfo('sdfgsdfghjvbdzfe', 349),
  createGeneInfo('ah34543fdvs', 61),
  createGeneInfo('aes4rggxfdf', 61),
  createGeneInfo('bhjklkbhygbkj', 61),
  createGeneInfo('btvouvlbhuio', 61),
];

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
  if (b[orderBy] < a[orderBy]) {
    return -1;
  }
  if (b[orderBy] > a[orderBy]) {
    return 1;
  }
  return 0;
}

type Order = 'asc' | 'desc';

function getComparator<Key extends keyof any>(
  order: Order,
  orderBy: Key,
): (
  a: { [key in Key]: number | string },
  b: { [key in Key]: number | string },
) => number {
  return order === 'desc'
    ? (a, b) => descendingComparator(a, b, orderBy)
    : (a, b) => -descendingComparator(a, b, orderBy);
}

// Since 2020 all major browsers ensure sort stability with Array.prototype.sort().
// stableSort() brings sort stability to non-modern browsers (notably IE11). If you
// only support modern browsers you can replace stableSort(exampleArray, exampleComparator)
// with exampleArray.slice().sort(exampleComparator)
function stableSort<T>(array: readonly T[], comparator: (a: T, b: T) => number) {
  const stabilizedThis = array.map((el, index) => [el, index] as [T, number]);
  stabilizedThis.sort((a, b) => {
    const order = comparator(a[0], b[0]);
    if (order !== 0) {
      return order;
    }
    return a[1] - b[1];
  });
  return stabilizedThis.map((el) => el[0]);
}

interface HeadCell {
  disablePadding: boolean;
  id: keyof GeneInfo;
  label: string;
  numeric: boolean;
}

const headCells: readonly HeadCell[] = [
  {
    id: 'hash',
    numeric: false,
    disablePadding: true,
    label: 'Hash',
  },
  {
    id: 'fitness',
    numeric: true,
    disablePadding: false,
    label: 'Fitness',
  },
];

interface EnhancedTableProps {
  numSelected: number;
  onRequestSort: (event: React.MouseEvent<unknown>, property: keyof GeneInfo) => void;
  onSelectAllClick: (event: React.ChangeEvent<HTMLInputElement>) => void;
  order: Order;
  orderBy: string;
  rowCount: number;
}

function EnhancedTableHead(props: EnhancedTableProps) {
  const { onSelectAllClick, order, orderBy, numSelected, rowCount, onRequestSort } =
    props;
  const createSortHandler =
    (property: keyof GeneInfo) => (event: React.MouseEvent<unknown>) => {
      onRequestSort(event, property);
    };

  return (
    <TableHead>
      <TableRow>
        <TableCell padding="checkbox">
          {/* <Checkbox
            color="primary"
            indeterminate={numSelected > 0 && numSelected < rowCount}
            checked={rowCount > 0 && numSelected === rowCount}
            onChange={onSelectAllClick}
            inputProps={{
              'aria-label': 'select all desserts',
            }}
          /> */}
        </TableCell>
        {headCells.map((headCell) => (
          <TableCell
            key={headCell.id}
            align={headCell.numeric ? 'right' : 'left'}
            padding={headCell.disablePadding ? 'none' : 'normal'}
            sortDirection={orderBy === headCell.id ? order : false}
          >
            <TableSortLabel
              active={orderBy === headCell.id}
              direction={orderBy === headCell.id ? order : 'asc'}
              onClick={createSortHandler(headCell.id)}
            >
              {headCell.label}
              {orderBy === headCell.id ? (
                <Box component="span" sx={visuallyHidden}>
                  {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                </Box>
              ) : null}
            </TableSortLabel>
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
}

interface EnhancedTableToolbarProps {
  numSelected: number;
}

function EnhancedTableToolbar(props: EnhancedTableToolbarProps) {
  const { numSelected } = props;

  return (
    <Toolbar
      sx={{
        pl: { sm: 2 },
        pr: { xs: 1, sm: 1 },
        ...(numSelected > 0 && {
          bgcolor: (theme) =>
            alpha(theme.palette.primary.main, theme.palette.action.activatedOpacity),
        }),
      }}
    >
      {numSelected > 0 ? (
        <Typography
          sx={{ flex: '1 1 100%' }}
          color="inherit"
          variant="subtitle1"
          component="div"
        >
          {numSelected} selected
        </Typography>
      ) : (
        <Typography
          sx={{ flex: '1 1 100%' }}
          variant="h6"
          id="tableTitle"
          component="div"
        >
          Genomes
        </Typography>
      )}
      {numSelected > 0 ? (
        <Tooltip title="Delete">
          <IconButton>
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      ) : (
        <Tooltip title="Filter list">
          <IconButton>
            <FilterListIcon />
          </IconButton>
        </Tooltip>
      )}
    </Toolbar>
  );
}

export default function EnhancedTable() {
  const connectionInfo = useContext(GlobalContext)
  const { sendMessage, lastMessage} = useWebSocket( 
    connectionInfo.wsConnection,
    {
      shouldReconnect: (closeEvent) => true
    }
    );

  const [count, setCount] = useState(30)
  const [msg, setMsg] = useState(
    "FT.AGGREGATE genomes * SORTBY 2 @fitness DESC LIMIT 0 10000 LOAD 2 hash fitness"
  )

  // const [geneList, setGeneList] = useState(0)
  const [rows, setRows] = useState(defaultRows)

  // setInterval(() => {
  //   sendMessage(msg)
  //   console.log("SENDING MSG")
  // }, 20000)


  // TODO: find a better way to do this -> this seems ugly lol
  const convertData = (d: string) => {
    let converted = []
    // console.log(d)
    // const raw: any = d.split(":").slice(2).join("\"").replaceAll("gene", "").trim().replaceAll(" ", "\",").replaceAll("]", " \"]")
    var raw: any = d
      .replace(msg + ":", "")
      .replaceAll("[fitness ", "{\"fitness\": ")
      .replaceAll("]", "\"}")
      .replaceAll("hash ", ", \"hash\": \"")
      .split(" ")
      .slice(2)
      .join(" ")
      .replaceAll("} {", "}, {")

    raw = raw.slice(0, raw.length - 2)
    raw = "[" + raw + "]"
    const data = JSON.parse(raw)
    return data
  }

  const getGenomes = () => {
      sendMessage("cmd;" + msg)
      console.log("SENDING MSG")
  }

  useEffect(() => {
    if (lastMessage != null) {
      console.log('got msg')
      const converted = convertData(lastMessage.data)
      setRows(converted)
    } else {
      getGenomes()
    }
  }, [lastMessage])

  const [order, setOrder] = React.useState<Order>('asc');
  const [orderBy, setOrderBy] = React.useState<keyof GeneInfo>('fitness');
  const [selected, setSelected] = React.useState<readonly string[]>([]);
  const [page, setPage] = React.useState(0);
  const [dense, setDense] = React.useState(false);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);

  const handleRequestSort = (
    event: React.MouseEvent<unknown>,
    property: keyof GeneInfo,
  ) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  // const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
  //   if (event.target.checked) {
  //     const newSelected = rows.map((n) => n.hash);
  //     setSelected(newSelected);
  //     return;
  //   }
  //   setSelected([]);
  // };

  const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
    const selectedIndex = selected.indexOf(name);
    let newSelected: readonly string[] = [];

    // TODO: This might be buggy in some edge cases
    if (selectedIndex === -1) {
      newSelected = [name]
    } else if (selectedIndex === 0) {
      newSelected = selected.slice(1);
    } else if (selectedIndex === selected.length - 1) {
      newSelected = selected.slice(0, -1);
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }

    // if (selectedIndex === -1) {
    //   newSelected = newSelected.concat(selected, name);
    // } else if (selectedIndex === 0) {
    //   newSelected = newSelected.concat(selected.slice(1));
    // } else if (selectedIndex === selected.length - 1) {
    //   newSelected = newSelected.concat(selected.slice(0, -1));
    // } else if (selectedIndex > 0) {
    //   newSelected = newSelected.concat(
    //     selected.slice(0, selectedIndex),
    //     selected.slice(selectedIndex + 1),
    //   );
    // }

    setSelected(newSelected);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleChangeDense = (event: React.ChangeEvent<HTMLInputElement>) => {
    setDense(event.target.checked);
  };

  const isSelected = (name: string) => selected.indexOf(name) !== -1;

  // Avoid a layout jump when reaching the last page with empty rows.
  const emptyRows =
    page > 0 ? Math.max(0, (1 + page) * rowsPerPage - rows.length) : 0;

  return (

    <Box sx={{ width: '100%' }}>
      <Tooltip title="Reload">
        <Button onClick={getGenomes} startIcon={<ReplayIcon/>}></Button>
      </Tooltip>
      <FormControlLabel
        control={<Switch checked={dense} onChange={handleChangeDense} />}
        label="Dense padding"
      />
      <Paper sx={{ width: '100%', mb: 2 }}>
        <EnhancedTableToolbar numSelected={selected.length} />
        <TableContainer>
          <Table
            sx={{ minWidth: 750 }}
            aria-labelledby="tableTitle"
            size={dense ? 'small' : 'medium'}
          >
            <EnhancedTableHead
              numSelected={selected.length}
              order={order}
              orderBy={orderBy}
              onSelectAllClick={() => {console.log('this is not currently available')}}
              // onSelectAllClick={handleSelectAllClick}
              onRequestSort={handleRequestSort}
              rowCount={rows.length}
            />
            <TableBody>
              {stableSort(rows, getComparator(order, orderBy))
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row, index) => {
                  const isItemSelected = isSelected(row.hash);
                  const labelId = `enhanced-table-checkbox-${index}`;

                  return (
                    <TableRow
                      hover
                      onClick={(event) => handleClick(event, row.hash)}
                      // role="checkbox" -> NOT RLLY NEEDED
                      // aria-checked={isItemSelected}
                      tabIndex={-1}
                      key={row.hash}
                      selected={isItemSelected}
                    >
                      <TableCell padding="checkbox">
                        {/* <Checkbox
                          color="primary"
                          checked={isItemSelected}
                          inputProps={{
                            'aria-labelledby': labelId,
                          }}
                        /> */}
                      </TableCell>
                      <TableCell
                        component="th"
                        id={labelId}
                        scope="row"
                        padding="none"
                      >
                        {row.hash}
                      </TableCell>
                      <TableCell align="right">{row.fitness}</TableCell>
                    </TableRow>
                  );
                })}
              {emptyRows > 0 && (
                <TableRow
                  style={{
                    height: (dense ? 33 : 53) * emptyRows,
                  }}
                >
                  <TableCell colSpan={6} />
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={rows.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
}



// function GeneBox() {
//   const connectionInfo = useContext(GlobalContext)
//   const { sendMessage, lastMessage} = useWebSocket( 
//     connectionInfo.wsConnection,
//     {
//       shouldReconnect: (closeEvent) => true
//     }
//     );

//   const [count, setCount] = useState(30)
//   const [msg, setMsg] = useState("cmd;KEYS gene:7*")

//   const [geneList, setGeneList] = useState(0)

//   setInterval(() => {
//     sendMessage(msg)
//     console.log("SENDING MSG")
//   }, 20000)


//   const convertData = (d: string) => {
//     let converted = []
//     // console.log(d)
//     const raw: any = d.split(":").slice(2).join("\"").replaceAll("gene", "").trim().replaceAll(" ", "\",").replaceAll("]", " \"]")
//     console.log(raw)
//     const data = JSON.parse(raw)
//     return data
//   }

//   useEffect(() => {
//     if (lastMessage != null) {
//       console.log('got msg')
//       const converted = convertData(lastMessage.data)
//       setGeneList(converted)

//     } else {
//       sendMessage(msg)
//       console.log("SENDING MSG")
//     }
//   }, [lastMessage])

// }