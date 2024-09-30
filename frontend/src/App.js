import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [playersFile, setPlayersFile] = useState(null);
  const [constraintsFile, setConstraintsFile] = useState(null);
  const [outputFile, setOutputFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const formData = new FormData();
    formData.append('players', playersFile);
    formData.append('constraints', constraintsFile);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setOutputFile(response.data.output_file);
    } catch (error) {
      console.error('Error uploading files:', error);
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h2 className="text-2xl font-bold mb-4">Soccer Team Sorter</h2>
                <form onSubmit={handleSubmit}>
                  <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="players">
                      Players File
                    </label>
                    <input
                      type="file"
                      id="players"
                      onChange={(e) => setPlayersFile(e.target.files[0])}
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    />
                  </div>
                  <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="constraints">
                      Constraints File
                    </label>
                    <input
                      type="file"
                      id="constraints"
                      onChange={(e) => setConstraintsFile(e.target.files[0])}
                      className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <button
                      type="submit"
                      className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                      disabled={isLoading || !playersFile || !constraintsFile}
                    >
                      {isLoading ? 'Processing...' : 'Sort Teams'}
                    </button>
                  </div>
                </form>
                {outputFile && (
                  <div className="mt-4">
                    <a
                      href={`/api/download/${outputFile}`}
                      className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                      download
                    >
                      Download Output
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;