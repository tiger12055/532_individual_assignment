# Load required libraries
library(tidyr)
library(dplyr)
library(leaflet)
library(shinydashboard)
library(maps)
library(scales)
library(ggplot2)
library(fresh)

# Read the data file
df1 <- read.csv(file = 'data/raw/HousingData.csv')

mytheme <- create_theme(
  adminlte_color(
    light_blue = "#FF3364"
  )
)

# Clean and filter the data
df_ <- df1 %>%
  tidyr::drop_na(bedrooms, bathrooms, sqft_living, price,
                 lat, long) %>%
  dplyr::filter(sqft_living >= 200, sqft_living <= 10000, price >= 200, price <= 600000) %>%
  dplyr::select(lat, long, price, sqft_living, bedrooms, bathrooms, condition, grade, zipcode, floors)

ui <- shinydashboard::dashboardPage(
  
  # Define the header
  shinydashboard::dashboardHeader(
    title = "Seattle Housing Listings"
  ),
  
  # Define the sidebar
  shinydashboard::dashboardSidebar(
    shiny::fluidRow(
      shiny::column(width = 12,
                    shiny::sliderInput("price", label = "Price:",
                                       min = min(df_$price), max = max(df_$price),
                                       value = c(min(df_$price),
                                                 max(df_$price)),
                                       step = 500),
                    
                    shiny::sliderInput("bedrooms", label = "Number of bedrooms:",
                                       min = min(df_$bedrooms), max = max(df_$bedrooms),
                                       value = c(min(df_$bedrooms),
                                                 min(df_$bedrooms)),
                                       step = 1),
                    
                    shiny::sliderInput("bathrooms", label = "Number of bathrooms:",
                                       min = min(df_$bathrooms), max = max(df_$bathrooms),
                                       value = c(min(df_$bathrooms),
                                                 min(df_$bathrooms)),
                                       step = 0.25),
                    
                    
                    shiny::sliderInput("sqft_living", label = "Square feet:",
                                       min = min(df_$sqft_living), max = max(df_$sqft_living),
                                       value = c(min(df_$sqft_living),
                                                 max(df_$sqft_living)),
                                       step = 1000)
      )
    ),
    # Change sidebar background color and font color
    tags$style(HTML('
      .main-sidebar {
        background-color: #666666;
      }
      .sidebar-menu li a {
        color: #FFFFFF;
      }
      .sidebar-menu li.active a {
        background-color: #4d4d4d;
      }
    '))
  ),
  
  # Define the body
  shinydashboard::dashboardBody(
    
    use_theme(mytheme),
    
    # Define the map box
    shiny::fluidRow(
      shiny::column(width = 12,
                    shinydashboard::box(width = 12, solidHeader = TRUE,
                                        leaflet::leafletOutput("map", width = '100%')
                    )
      )
    ),
    
    # Define the data table and price histogram boxes
    shiny::fluidRow(
      shiny::column(width = 6,
                    shinydashboard::box(width = 12, solidHeader = TRUE,
                                        DT::dataTableOutput("data_table")
                    )
      ),
      shiny::column(width = 6,
                    shinydashboard::box(width = 12, solidHeader = TRUE,
                                        shiny::plotOutput("price_histogram")
                    )
      )
    ),
    
    # Change box border and background color
    tags$style(HTML('
      .box {
        background-color: #FFFFFF;
        border: 2px solid #4d4d4d;
      }
    '))
    
  )
  
)

# Define the server logic
server <- function(input, output) {
  
  # Create a reactive dataset based on user inputs
  data <- shiny::reactive({
    df_ %>%
      dplyr::filter(bedrooms >= input$bedrooms[1] & bedrooms <= input$bedrooms[2],
                    bathrooms >= input$bathrooms[1] & bathrooms <= input$bathrooms[2],
                    
                    sqft_living >= input$sqft_living[1] & sqft_living <= input$sqft_living[2],
                    
                    price >= input$price[1] & price <= input$price[2])
  })
  
  # render the map
  output$map <- leaflet::renderLeaflet({
    data() %>%
      leaflet::leaflet() %>%
      leaflet::addTiles() %>%
      leaflet::addCircles(lng = ~long, lat = ~lat,
                          opacity = .7,
                          color = '#3399FF',
                          radius = 10,
                          # Add tooltip to show price and sqft_living information
                          label = ~paste0("Price: ", scales::dollar(price), "   ",
                                          "Sqft Living: ", scales::comma(sqft_living)))
  })
  
  # Render the data table
  output$data_table <- DT::renderDataTable(
    data() %>%
      dplyr::select(price, bedrooms, bathrooms, sqft_living, condition) %>%
      
      dplyr::mutate(price = scales::dollar(price), sqft_living = scales::comma(sqft_living)),
    options = list(pageLength = 5,
                   dom = 'tipr',
                   scrollX = TRUE,
                   searching = FALSE))
  
  output$price_histogram <- shiny::renderPlot({
    data() %>%
      ggplot2::ggplot(ggplot2::aes(x = price)) +
      ggplot2::geom_histogram(binwidth = 5000, color = "white", fill = "#3399FF") +
      ggplot2::labs(title = "Price Distribution", x = "Price", y = "Count") +
      ggplot2::scale_x_continuous(labels = scales::dollar)
  })
  
}

# # Run the application 
shiny::shinyApp(ui = ui, server = server)