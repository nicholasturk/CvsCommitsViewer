<template>
   <div id="home" class="mt-3">
      <h4 class="border-bottom pb-3">CVS checkin search <b-button class="float-right pb-1 pt-1" @click="reset" variant="danger">Reset</b-button></h4>
      <b-row class="mb-3 mt-3">
        <b-col sm="3" class="pr-0">
          <label class="labh"> <span :class="{ 'labli': suggestionsLoading }" >Ticket:</span><b-spinner small v-if="suggestionsLoading"></b-spinner> </label> 
          <vue-autosuggest 
            ref="autosuggest" 
            type="search"
            class="inline-block"
            name="ih"
            v-model="ticketSearch"
            @keyup.enter="search()"
            @input="onInputChage"
            :suggestions="filteredOptions.tickets" 
            :input-props="inputProps.tickets" 
            :get-suggestion-value="getSuggestionValueTicket"
            :limit="100">
          </vue-autosuggest>
        </b-col>
        <b-col sm="3" class="pr-0">
          <label class="labh"> <span :class="{ 'labli': suggestionsLoading }" >File:</span><b-spinner small v-if="suggestionsLoading"></b-spinner> </label> 
          <vue-autosuggest 
            ref="autosuggest" 
            type="search"
            v-model="fileSearch"
            @keyup.enter="search()"
            @input="onInputChage"
            :suggestions="filteredOptions.files" 
            :input-props="inputProps.files" 
            :get-suggestion-value="getSuggestionValueFileName"
            :limit="100">
          </vue-autosuggest>
        </b-col>
        <b-col sm="3" class="pr-0">
          <label class="labh"> <span :class="{ 'labli': suggestionsLoading }" >Author:</span><b-spinner small v-if="suggestionsLoading"></b-spinner> </label> 
          <vue-autosuggest 
            ref="autosuggest" 
            type="search"
            v-model="authorSearch"
            @keyup.enter="search()"
            @input="onInputChage"
            :suggestions="filteredOptions.authors" 
            :input-props="inputProps.authors" 
            :show-dropdowns="true"
            :get-suggestion-value="getSuggestionValueAuthor"
            :limit="100">
          </vue-autosuggest>
        </b-col>
        <b-col sm="3" class="pr-0">
          <label class="labh"> <span :class="{ 'labli': suggestionsLoading }" >Select Range:</span><b-spinner small v-if="suggestionsLoading"></b-spinner> </label> 
          <date-range-picker
            ref="dp"
            v-model="choices.dateRange" 
          ></date-range-picker>
        </b-col>
      </b-row>
      <b-spinner class="text-center" v-if="loading"></b-spinner>
      <div v-if="!loading && hasSearched">
        <b-row>
          <b-col sm="12">
            <div class=""><b>{{ commits.length }}</b> results
            <b-icon icon="chevron-left" @click="prev">Prev</b-icon>
            <span class="paginationNumbers">{{ totalPages == 0 ? 0 : pagination.currentPage  }}/{{ totalPages }} </span>
            <b-icon icon="chevron-right" @click="next">Next</b-icon></div>
          </b-col>
          <b-col sm="12" class="mt-1">
          </b-col>
        </b-row>
        <div class="results" v-if="commitsSorted.length > 0"> 
          <b-row class="mb pb-1 pt-3" v-for="(commit, idx) in commitsSorted" :key="(commit, idx)">
            <b-col>
              <div class="ml-2 mt-1 border-left pl-2">
                <div v-for="(k, i) in Object.keys(commit)" :key="(k, i)">
                  <div v-if="k != '_id'">
                    <span v-if="k == 'file_path'" :set="file = getFileSplit(commit[k])">
                      {{ k }}:
                      <span> {{ file[0] }}<b>{{ file[1] }}</b> </span>
                    </span>
                    <span v-else-if="k == 'message'">
                      {{ k }}:
                      <span> "{{ commit[k] }}" </span>
                    </span>
                    <span v-else>
                      {{ k }}:
                      <span> {{ commit[k] }} </span>
                    </span>
                  </div>
                </div>
              </div>
            </b-col>
          </b-row>
        </div>
      </div>
   </div>
</template>

<script>

const url = "****************"

import axios from 'axios';
import 'vue2-daterange-picker/dist/vue2-daterange-picker.css'
import DateRangePicker from 'vue2-daterange-picker';

export default{

  name: 'search',

  components: { DateRangePicker },

  data(){
    return{
      ticketSearch: '',g=
      authorSearch: '',
      fileSearch: '',
      choices: {
        ticket: null,
        author: null,
        file_name: null,
        dateRange: {
          startDate: '',
          endDate: ''
        }
      },
      suggestionsLoading: false,
      currSearching: 'tickets',
      commits: [],
      suggestions: {},
      loading: false,
      filteredOptions: {
        tickets: [],
        authors: [],
        files: []
      },
      numResults: null,
      inputProps: {
          tickets: {
            id: "autosuggest__input__tickets",
            class: 'autosuggest__input',
            placeholder: "Choose ticket",
            onInputChange: this.onInputChange
          },
          authors: {
            id: "autosuggest__input__authors",
            class: 'autosuggest__input',
            placeholder: "Choose author",
            onInputChange: this.onInputChange
          },
          files: {
            id: "autosuggest__files",
            class: 'autosuggest__input',
            placeholder: "Choose file",
            onInputChange: this.onInputChange
          },
      },
      hasSearched: false,
      pagination: {
        currentPage: 1,
        postsPerPage: 3
      }
    }
  },

  async mounted(){
    if (this.$route.params.token){
      this.choices.ticket = this.$route.params.token.toUpperCase();
      this.search();
    }
    this.getSuggestions()
  },

  methods: {

    reset(){
      this.ticketSearch = ''
      this.authorSearch = ''
      this.fileSearch = ''
      this.choices.ticket = ''
      this.choices.author = ''
      this.choices.file_name = ''
      this.choices.dateRange.startDate = ''
      this.choices.dateRange.endDate = ''
      document.querySelector('.reportrange-text span').textContent = '-'
      this.commits = []
    },

    async getSuggestions(){
      this.suggestionsLoading = true
      this.suggestions = (await axios.post(`${url}api/suggestions`, this.choices)).data
      this.filteredOptions = {...this.suggestions}
      this.suggestionsLoading = false
    },

    search(){
      this.hasSearched = true;
      this.loading = true;
      this.pagination.currentPage = 1;
      axios.post(`${url}api/search`, this.choices).then(res => { 
        this.commits = res.data 
        this.loading = false;
      })
    },

    getFileSplit(str){
      var arr = str.split('/')
      var a = arr.splice(0, arr.length - 1).join('/')
      var b = arr[arr.length - 1]
      if (arr.length == 1)a+='/'
      return [a, b]
    },

    onInputChage(text) {

      if (text == '' || text == undefined){
        return this.filteredOptions = {...this.suggestions}
      }

      const filteredData = this.suggestions[this.currSearching][0].data.filter(item => {
        return item.toLowerCase().indexOf(text.toLowerCase()) > -1;
      }).slice(0, 100);
      
      this.filteredOptions[this.currSearching] = [{data: filteredData}];

    },

    getSuggestionValueTicket(suggestion) {
      this.ticketSearch = suggestion.item;
      this.choices.ticket = suggestion.item;
      this.getSuggestions();
      this.search();
    },

    getSuggestionValueAuthor(suggestion) {
      this.authorSearch = suggestion.item;
      this.choices.author = suggestion.item;
      this.getSuggestions();
      this.search();
    },

    getSuggestionValueFileName(suggestion) {
      this.fileSearch = suggestion.item;
      this.choices.file_name = suggestion.item;
      this.getSuggestions();
      this.search();
    },

    next(){
      if (this.pagination.currentPage < this.totalPages) {
        this.pagination.currentPage++
      }
    },

    prev () {
      if (this.pagination.currentPage > 1) {
        this.pagination.currentPage--
      }
    }

  },

  computed: {

    totalPages(){
      return Math.ceil(this.commits.length / this.pagination.postsPerPage)
    },

    commitsSorted(){
      var temp = this.commits;
      return temp.slice((this.pagination.currentPage - 1) * this.pagination.postsPerPage, this.pagination.currentPage * this.pagination.postsPerPage )
    }
  },

  watch: {
    ticketSearch(){
      this.currSearching = 'tickets'
      if(this.ticketSearch == '') {
        this.choices.ticket = null
        this.search()
        this.getSuggestions() 
      }
    },
    authorSearch(){
      this.currSearching = 'authors'
      if(this.authorSearch == ''){ 
        this.choices.author = null
        this.search()
        this.getSuggestions() 
      }
    },
    fileSearch(){
      this.currSearching = 'files'
      if(this.fileSearch == ''){ 
        this.choices.file_name = null
        this.search()
        this.getSuggestions() 
      }
    },

    'choices.dateRange.startDate'(){
      if(this.choices.dateRange.startDate != '') document.querySelector('.reportrange-text span').textContent = this.$refs.dp.rangeText;
      this.getSuggestions()
      this.search()
    },

    'choices.dateRange.endDate'(){
      if(this.choices.dateRange.endDate != '') document.querySelector('.reportrange-text span').textContent = this.$refs.dp.rangeText;
    }
  }

};

</script>

<style>

  #home{
    padding-top: 50px;
    padding-bottom: 300px;
  }

  label{
    font-weight: 500;
  }

  .autosuggest__input {
    outline: none;
    position: relative;
    display: inline-block;
    font-size: 15px;
    height: 40px;
    border: 1px solid rgb(204, 204, 204);
    border-radius: 5px;
    padding: 5px;
    width: 100%;
    box-sizing: border-box;
    -webkit-box-sizing: border-box;
    -moz-box-sizing: border-box;
  }

  .autosuggest__results{
    width: 150%;
  }

  .labh span{
    margin-left: 10px;
    margin-bottom: 2px;
  }

  .vue-daterange-picker{
    width: 100%;
  }

  .labli{
    color: lightgray;
  }

  .autosuggest__input:focus{
    border: 2px solid rgb(49, 49, 49)
  }

  .b-icon{
    cursor: pointer;
  }

  .dataitem{
    font-weight:400
  }

  .paginationNumbers{
    user-select: none;
    min-width: 300px;
  }


  .fc{
    font-weight:600;
    font-size: 16px;
  }

  .fb{
    font-weight: 600
  }

  button{
    padding: 5px;
  }
  
  #autosuggest__input.autosuggest__input-open {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }
  
  .autosuggest__results-container {
    position: relative;
    width: 100%;
  }

  li{
    padding-left: 20px;
    padding-top: 5px;
    border-bottom: 1px solid rgb(255, 237, 237);
    cursor: pointer;
  }

  li:hover{
    background-color:lightgray;
  }
  
  .autosuggest__results {
    font-weight: 300;
    margin: 0;
    position: absolute;
    z-index: 10000001;
    width: 150%;
    border: 1px solid #e0e0e0;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
    background: white;
    padding: 0px;
    overflow: scroll;
    max-height: 400px;
  }
  
  .autosuggest__results ul {
    list-style: none;
    padding-left: 0;
    margin: 0;
  }
  
  .autosuggest__results .autosuggest__results_item {
    cursor: pointer;
    padding: 15px;
  }
  
  #autosuggest ul:nth-child(1) > .autosuggest__results_title {
    border-top: none;
  }
  
  .autosuggest__results .autosuggest__results_title {
    color: gray;
    font-size: 11px;
    margin-left: 0;
    padding: 15px 13px 5px;
    border-top: 1px solid lightgray;
  }
  
  .autosuggest__results .autosuggest__results_item:active,
  .autosuggest__results .autosuggest__results_item:hover,
  .autosuggest__results .autosuggest__results_item:focus,
  .autosuggest__results .autosuggest__results_item.autosuggest__results_item-highlighted {
    background-color: #ddd;
  }
</style>
