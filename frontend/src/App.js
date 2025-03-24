import React, { useState } from 'react';
import { 
  Container, 
  Paper, 
  Typography, 
  Button, 
  TextField, 
  Box, 
  Alert, 
  Grid, 
  Card, 
  CardContent, 
  CircularProgress, 
  List, 
  ListItem, 
  ListItemText, 
  Divider 
} from '@mui/material';
import { Upload, Check } from '@mui/icons-material';
import axios from 'axios';

function App() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);

  const handleCodeChange = (e) => {
    setCode(e.target.value);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const validExtensions = ['.py', '.js', '.jsx'];
      const fileExtension = `.${selectedFile.name.split('.').pop().toLowerCase()}`;
      if (!validExtensions.includes(fileExtension)) {
        setError('Invalid file type. Only .py, .js, and .jsx files are supported.');
        return;
      }
      setFile(selectedFile);
    }
  };

  const analyzeCode = async () => {
    if (!code && !file) {
      setError('Please enter code or upload a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await axios.post('http://localhost:8000/api/v1/upload-code', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        setAnalysis(response.data);
      } else {
        const response = await axios.post('http://localhost:8000/api/v1/code-review', {
          code,
          language
        });
        setAnalysis(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error analyzing code');
    } finally {
      setLoading(false);
    }
  };

  const formatScore = (score) => {
    return `${Math.round(score)}%`;
  };

  const renderAnalysis = () => {
    if (!analysis) return null;

    return (
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Code Analysis Results
          </Typography>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Score
              </Typography>
              <Typography variant="h4" component="div" sx={{ color: analysis.overall_score >= 70 ? 'success.main' : 'error.main' }}>
                {formatScore(analysis.overall_score)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Breakdown
              </Typography>
              <List>
                {Object.entries(analysis.breakdown).map(([category, score]) => (
                  <ListItem key={category}>
                    <ListItemText
                      primary={category}
                      secondary={formatScore(score)}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recommendations
              </Typography>
              <List>
                {analysis.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Feedback
              </Typography>
              <Typography>
                {analysis.detailed_feedback}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Code Reviewer
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 4 }}>
          <Button
            variant="contained"
            component="label"
            startIcon={<Upload />}
            sx={{ mr: 2 }}
          >
            Upload File
            <input
              type="file"
              hidden
              accept=".py,.js,.jsx"
              onChange={handleFileChange}
            />
          </Button>

          <TextField
            select
            label="Language"
            value={language}
            onChange={handleLanguageChange}
            sx={{ width: 200, ml: 2 }}
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="jsx">JSX</option>
          </TextField>
        </Box>

        <TextField
          multiline
          rows={15}
          fullWidth
          label="Enter your code here"
          value={code}
          onChange={handleCodeChange}
          sx={{ mb: 4 }}
        />

        <Button
          variant="contained"
          color="primary"
          onClick={analyzeCode}
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <Check />}
          sx={{ mb: 4 }}
        >
          Analyze Code
        </Button>

        {renderAnalysis()}
      </Paper>
    </Container>
  );
}

export default App;