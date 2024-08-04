import { createSQLiteHTTPPool, SQLiteHTTPPool } from "sqlite-wasm-http";
import { ConsumptionTypeDto, LocationDto, PriceDto, ServiceDto } from "./types/types";


export default class Database {

    private pool!: SQLiteHTTPPool

    async init(){
        const remoteURL = import.meta.env.BASE_URL + 'test_new.sqlite';
        this.pool = await createSQLiteHTTPPool({ workers: 4 });
        await this.pool.open(remoteURL);
    }

    async getServices(): Promise<ServiceDto[]> {
        const servicesResult = await this.pool.exec('SELECT id, name FROM azure_services ORDER BY name ASC');
        return servicesResult.map(r => ({id: r.row[0] as string, name: r.row[1] as string}))
    }

    async getLocations(): Promise<LocationDto[]> {
        const locationsResult = await this.pool.exec('SELECT id, name FROM azure_locations ORDER BY name ASC');
        return locationsResult.map(r => ({id: r.row[0] as string, name: r.row[1] as string}))
    }

    async getConsumptionTypes(): Promise<ConsumptionTypeDto[]> {
        const results = await this.pool.exec('SELECT id, name FROM azure_consumption_types ORDER BY name ASC');
        return results.map(r => ({id: r.row[0] as string, name: r.row[1] as string}))
    }

    async getPrices(service: string, location: string, consumptionType: string): Promise<PriceDto[]> {
        console.log(service, location)
        const result = await this.pool.exec(`
SELECT 
    azure_price_points.retail_price, 
    azure_price_points.unit_of_measure,
    azure_products.name
FROM azure_price_points 

INNER JOIN azure_products
ON azure_price_points.product_id = azure_products.id
WHERE 
    azure_price_points.service_id = $service 
    AND azure_price_points.location_id = $location
    AND azure_price_points.consumption_type_id = $consumptionType
LIMIT 20
`,
{
    $location: location,  
    $service: service,
    $consumptionType: consumptionType
 },);
        return result.map(r => ({
            retailPrice: r.row[0] as number,
            unit: r.row[1] as string,
            productName: r.row[2] as string,
            // consumptionType: r.row[3] as string,
        }))
    }

    async dispose(){
        await this.pool.close();
    }

  }