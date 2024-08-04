export interface Base {
    id: string
}

export interface NameBase {
    id: string
    name: string
}

export interface ServiceDto extends NameBase {
}

export interface LocationDto extends NameBase {
}


export interface ConsumptionTypeDto extends NameBase {
}

export interface PriceDto {
    retailPrice: number
    unit: string
    productName: string
}