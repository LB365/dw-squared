### dw-squared

A wrapper of the Datawrapper python client, whence datawrapper squared

### Run the tests

Run

```shell
pytest -s tests tests/test_client.py --token <your-datawrapper-token>
pytest -s tests tests/test_transform.py
```


### Mapping example

Provide a mapping config file as a `.yaml` file.

#### Seasonal

```yaml
- 
  chart_type : "seasonal"
  title: "chart-seasonal" 
  source: "Source"
  notes: "A Note in the bottom"
  height: 600
  width: 600
  freq_graph: 'W'
  unfold: True
  aggregation_freq_graph: 'mean'
  interpolation: 'linear'
  cutoff_year: 2020
  prefix_unit: "USD"
  display_today: true
  graph_start: (date "2015-1-1")
  graph_end: null
  series: 
    - 
      series_id: "my series"
      legend: "a legend"
      start: (deltayears (today) -10)
      end: null
      revision: null

```

#### Line

```yaml
- 
  chart_type : "line"
  title: "chart-line" 
  source: "source"
  notes: null
  height: 400
  width: 600
  prefix_unit: "USD"
  series: 
    - 
      series_id: "series1"
      legend: "hello"
      start: (deltamonths (yearstart (today)) -2)
      end: (yearend (today))
      revision: null
    - 
      series_id: "series2"
      legend: "hello2"
      start: (deltamonths (yearstart (today)) -2)
      end: (yearend (today))
      revision: null
```

#### Line with secondary axis

```yaml
- 
  chart_type : "line"
  title: "chart-line" 
  source: "source"
  notes: null
  height: 400
  width: 600
  today_line: False
  secondary: True
  secondary_unit: 'USD per onces'
  prefix_unit: "GBP per ton"
  series: 
    - 
      series_id: "series1"
      legend: "hello"
      start: (deltamonths (yearstart (today)) -2)
      end: (yearend (today))
      revision: null
    - 
      series_id: "series2"
      legend: "hello2"
      start: (deltamonths (yearstart (today)) -2)
      end: (yearend (today))
      revision: null
```

