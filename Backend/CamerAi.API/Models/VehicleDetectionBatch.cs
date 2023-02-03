using CamerAi.DAL.DTOs;

namespace CamerAi.API.Models;

public sealed class VehicleDetectionBatch
{
    public IEnumerable<Detection> Detections { get; set; }
    public string MacAddress { get; set; }
    public double Latitude { get; set; }
    public double Longitude { get; set; }
} 