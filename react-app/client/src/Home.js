import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Home(){
  const [data, setData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortConfig, setSortConfig] = useState({ key: '', direction: '' });
  const [searchScope, setSearchScope] = useState('all');
  const [visible, setVisible] = useState(20);
  const [expandedRows, setExpandedRows] = useState({});
  const showMoreItems = () => {
    setVisible(prevValue => prevValue + 20);
  };
  const [selectedData, setSelectedData] = useState({});
  const [show, setShow] = useState(false);
  const handleClick = (selectedData) => {
    setSelectedData(selectedData);
    setShow(true);
  };

  const hideModal = () => {
    setShow(false);
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

  const handleRowClick = (index) => {
    setExpandedRows(prevExpandedRows => ({
      ...prevExpandedRows,
      [index]: !prevExpandedRows[index]
    }));
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
    const predictionString = row.prediction === 0 ? 'reliable' : 'fake';
    const matchesFilter = filterType === 'all' ||
      (filterType === 'correct' && predictionString === row.type) ||
      (filterType === 'incorrect' && predictionString !== row.type);
    return matchesSearchTerm && matchesFilter;
  });
    return (
        <div className = "Home">
            <h1>Categorization Results</h1>
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
                Correct predictions
                </label>
                <label>
                <input
                    type="radio"
                    value="incorrect"
                    checked={filterType === 'incorrect'}
                    onChange={handleFilterChange}
                />
                Incorrect predictions
                </label>
            </div>
            <table className="prediction-table">
                <thead>
                {!show && (<tr>
                    <th onClick={() => handleSort('title')}>Title</th>
                    <th>Predicted Type</th>
                    <th onClick={() => handleSort('type')}>Actual Type</th>
                    <th>Content</th>
                </tr>)}
                </thead>
                <tbody>
                {filteredData.slice(0, visible).map((row, index) => (
                    <tr key={index}>
                    <td className='title-content'>{row.title}</td>
                    <td>{row.prediction === 0 ? 'reliable' : 'fake'}</td>
                    <td>{row.type}</td>
                    <td>{shortenText(row.content, 200)}
                        <button className='viewContentButton' onClick={() => handleClick(row)}>View full content</button>
                    </td>
                    </tr>
                ))}
                </tbody>
            </table>
            {show && <Modal details={selectedData} handleClose={hideModal} />}
            <button className='loadMoreButton' onClick={showMoreItems}>{"Load more"}</button>
            <div>
                <p>Primary dataset:
                <a href="https://github.com/several27/FakeNewsCorpus"> Fake News Corpus </a> </p>
                <p>Total: 28.6GB (3,835,102 fake, 1,920,139 reliable)</p>
                <p>Drop 50% of the fake articles, since there are twice as many in the dataset (3,835,102) vs. reliable articles (1,920,139). We don’t want our model to be biased towards predicting news as fake.
                </p>
                <p>
                Clean the dataset: remove entries with any NULL fields, or have an “unknown” type.
                </p>
                <p>This process took ~30 minutes to run</p>

                <p>Afterwards, we transformed datasets into features using TF-IDF, trained it using binomial logistic regression, tuned it using k-fold cross validation, and tested it on the test dataset.</p>
                <p>We got a ~90% accuracy in correctly news classification. It took ~20 minutes to complete the process using 4 spark executors</p>
            </div>
      </div>
    );
    
}
const Modal = ({ handleClose, details }) => {
    return (
      <div className='modalDisplayBlock'>
        <div className='popupInner'>
          <h3>{details?.title}</h3>
          <p>Predicted Value: {details?.prediction === 0 ? 'reliable' : 'fake'}</p>
          <p>Actual Value: {details?.type}</p>
          <p className='innerContent'>{details?.content}</p>
          <button className='closeButton' onClick={handleClose}>
            Close
          </button>
        </div>
      </div>
    );
  };

function getCount({filteredData}){
    // const filteredData = sortedData.filter((row) => {
    // const searchTarget = searchScope === 'all' ?
    //     `${row.title} ${row.type} ${row.content} ${row.prediction}` :
    //     row.title;
    // const matchesSearchTerm = searchTarget.toLowerCase().includes(searchTerm.toLowerCase());
    // const predictionString = row.prediction === 0 ? 'reliable' : 'fake';
    // const matchesFilter = filterType === 'all' ||
    //     (filterType === 'correct' && predictionString === row.type) ||
    //     (filterType === 'incorrect' && predictionString !== row.type);
    // }
    
    return(
        <p>{filteredData.length}</p>
    );
}

export default Home