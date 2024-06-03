import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [data, setData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

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

  const shortenText = (text, maxLength) => {
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  const filteredData = data.filter((row) =>
    row.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    row.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    row.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
      <table className="prediction-table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Type</th>
            <th>Content</th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((row, index) => (
            <tr key={index}>
              <td>{row.title}</td>
              <td>{row.type}</td>
              <td>{shortenText(row.content, 200)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;