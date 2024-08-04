<script setup lang="ts">
import { Ref, ref, watch } from 'vue';
import Database from './Database';
import { LocationDto, ServiceDto, PriceDto, ConsumptionTypeDto} from './types/types';

let serviceMapping: Ref<{ [s: string]: ServiceDto }> = ref({})
let services: Ref<string[]> = ref([])
let locationMapping: Ref<{ [s: string]: LocationDto }> = ref({})
let locations: Ref<string[]> = ref([])
let consumptionTypeMapping: Ref<{ [s: string]: ConsumptionTypeDto }> = ref({})
let consumptionTypes: Ref<string[]> = ref([])
let prices: Ref<PriceDto[]> = ref([])

let database: Database

setTimeout(async () => {
  try {
    database = new Database()
    await database.init()

    const dbServices = await database.getServices()
    services.value = dbServices.map(s => s.id)
    serviceMapping.value = dbServices.reduce((services, service) => {
      return {
        ...services,
        [service.id]: service
      }
    }, {})

    const dbLocations = await database.getLocations()
    locations.value = dbLocations.map(l => l.id)
    locationMapping.value = dbLocations.reduce((locations, location) => {
      return {
        ...locations,
        [location.id]: location
      }
    }, {})

    const dbconsumptionTypes = await database.getConsumptionTypes()
    consumptionTypes.value = dbconsumptionTypes.map(l => l.id)
    consumptionTypeMapping.value = dbconsumptionTypes.reduce((consumptionTypes, consumptionType) => {
      return {
        ...consumptionTypes,
        [consumptionType.id]: consumptionType
      }
    }, {})

  } catch (e) {
    console.log(e)
  }
}, 0);

const selectService = ref('')
const selectLocation = ref('')
const selectConsumptionType = ref('')

watch(
  [selectService, selectLocation, selectConsumptionType],
  async ([service, location, consumptionType]) => {
    if (service && location && consumptionType) {
      prices.value = await database.getPrices(service, location, consumptionType)
    }
  }
)

</script>

<template>
  <div>
    <h1>
      Cloud Cost - Overview
    </h1>
    <div>
      <div>Service: {{ serviceMapping[selectService]?.name }}</div>
      <div>Location: {{ locationMapping[selectLocation]?.name }}</div>
    </div>
    <select v-model="selectService">
      <option disabled value="">Please select one</option>
      <option v-for="item in Object.keys(serviceMapping)" :value="item">{{ serviceMapping[item].name }}</option>
    </select>


    <select v-model="selectLocation">
      <option disabled value="">Please select one</option>
      <option v-for="locationId in locations" :value="locationId">{{ locationMapping[locationId].name }}</option>
    </select>

    <select v-model="selectConsumptionType">
      <option disabled value="">Please select one</option>
      <option v-for="consumptionId in consumptionTypes" :value="consumptionId">{{ consumptionTypeMapping[consumptionId].name }}</option>
    </select>

    <table>
      <thead>
        <tr>
          <th>Price</th>
          <th>Unit</th>
          <th>Product</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="price in prices">
          <td>{{ price.retailPrice }} USD</td>
          <td>{{ price.unit }}</td>
          <td>{{ price.productName }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped></style>
