import React from 'react'

function Predict(){
    return (
        <>
        <h1>Predicting New Articles</h1>
        <div className='article-box'>
        <input
            type="text"
            placeholder="Enter article here..."
            className="article-textbox"
        />
        <p>Predicted Type:</p>
        </div>
        </>
    )
}

export default Predict