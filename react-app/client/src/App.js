import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [data, setData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortConfig, setSortConfig] = useState({ key: '', direction: '' });
  const [searchScope, setSearchScope] = useState('all');
  const [visible, setVisible] = useState(20);
  const showMoreItems = () => {
    setVisible(prevValue => prevValue + 20)
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/predictions');
        setData(response.data);
      } catch (error) {
        console.error('Error fetching the data', error);
      }
    };
    fetchData();
  }, []);

  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };

  const handleFilterChange = (event) => {
    setFilterType(event.target.value);
  };

  const handleSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const handleSearchScopeChange = (event) => {
    setSearchScope(event.target.value);
  };

  const sortedData = [...data].sort((a, b) => {
    if (a[sortConfig.key] < b[sortConfig.key]) {
      return sortConfig.direction === 'ascending' ? -1 : 1;
    }
    if (a[sortConfig.key] > b[sortConfig.key]) {
      return sortConfig.direction === 'ascending' ? 1 : -1;
    }
    return 0;
  });

  const shortenText = (text, maxLength) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const filteredData = sortedData.filter((row) => {
    const searchTarget = searchScope === 'all' ?
      `${row.title} ${row.type} ${row.content} ${row.prediction}` :
      row.title;
    const matchesSearchTerm = searchTarget.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' ||
      (filterType === 'correct' && row.prediction === row.type) ||
      (filterType === 'incorrect' && row.prediction !== row.type);
    return matchesSearchTerm && matchesFilter;
  });

  return (
    <div className="App">
      <h1>Predictions</h1>
      <input
        type="text"
        placeholder="Enter phrase to sort the table..."
        value={searchTerm}
        onChange={handleSearch}
        className="search-bar"
      />
      <div className="search-scope">
        <label>
          <input
            type="radio"
            value="all"
            checked={searchScope === 'all'}
            onChange={handleSearchScopeChange}
          />
          Search All
        </label>
        <label>
          <input
            type="radio"
            value="title"
            checked={searchScope === 'title'}
            onChange={handleSearchScopeChange}
          />
          Search Title Only
        </label>
      </div>
      <div className="filter-options">
        <label>
          <input
            type="radio"
            value="all"
            checked={filterType === 'all'}
            onChange={handleFilterChange}
          />
          All
        </label>
        <label>
          <input
            type="radio"
            value="correct"
            checked={filterType === 'correct'}
            onChange={handleFilterChange}
          />
          Correct
        </label>
        <label>
          <input
            type="radio"
            value="incorrect"
            checked={filterType === 'incorrect'}
            onChange={handleFilterChange}
          />
          Incorrect
        </label>
      </div>
      <table className="prediction-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('title')}>Title</th>
            <th>Predicted Type</th>
            <th onClick={() => handleSort('type')}>Actual Type</th>
            <th>Content</th>
          </tr>
        </thead>
        <tbody>
            {filteredData.slice(0, visible).map((row, index) => (
              <tr key={index}>
                <td>{row.title}</td>
                <td>{row.prediction === 0 ? 'reliable' : 'fake'}</td>
                <td>{row.type}</td>
                <td>{shortenText(row.content, 200)}</td>
              </tr>
            ))}
        </tbody>
      </table>
      <button onClick = {showMoreItems}>{"Load more"}</button>
    </div>
  );
};

export default App;