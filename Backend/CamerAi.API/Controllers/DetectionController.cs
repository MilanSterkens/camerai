using CamerAi.API.EntityFramework;
using CamerAi.API.Models;
using CamerAi.DAL.DTOs;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CamerAi.API.Controllers;

[ApiController]
[Route("[controller]")]
public sealed class DetectionController : ControllerBase
{
    readonly CamerAiDbContext _dbContext;
    readonly ILogger<DetectionController> _logger;

    public DetectionController(CamerAiDbContext dbContext, ILogger<DetectionController> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    [HttpGet(Name = "GetDetections")]
    public async Task<ActionResult<IEnumerable<VehicleDetection>>> GetDetections()
    {
        if (_dbContext.Detections == null)
        {
            return NotFound();
        }

        return await _dbContext.Detections.ToListAsync();
    }

    [HttpPost(Name = "PostDetections")]
    public async Task<IActionResult> BatchData([FromBody] VehicleDetectionBatch detections)
    {
        _logger.LogInformation(
            $"Processing detections for {detections.MacAddress} received {detections.Detections.Count()} detections");

        var device = await _dbContext.Devices.FirstOrDefaultAsync(x => x.UniqueId == detections.MacAddress);
        if (device == null)
        {
            device = new Device
            {
                UniqueId = detections.MacAddress,
                Latitude = detections.Latitude,
                Longitude = detections.Longitude
            };
            _dbContext.Devices.Add(device);
            await _dbContext.SaveChangesAsync();
        }
        
        bool IsLocationChanged(double lat1, double lng1, double lat2, double lng2, double margin)
        {
            double latDiff = Math.Abs(lat1 - lat2);
            double lngDiff = Math.Abs(lng1 - lng2);

            return latDiff > margin || lngDiff > margin;
        }
        
        if (IsLocationChanged(device.Latitude, device.Longitude, detections.Latitude, detections.Longitude, 0.009))
        {
            device.Latitude = detections.Latitude;
            device.Longitude = detections.Longitude;

            for (int i = 1; i < 5; i++)
            {
                await _dbContext.VehicleDeviceMaxSpeeds.AddAsync(new VehicleDeviceMaxSpeed()
                {
                    MaxSpeed = 0,
                    Type = (VehicleType)i,
                    DeviceUniqueId = detections.MacAddress,
                    Latitude = detections.Latitude,
                    Longitude = detections.Longitude
                });
            }
            
        }
        
        
        foreach (var detection in detections.Detections)
        {
            var vehicleDeviceMaxSpeeds = await _dbContext.VehicleDeviceMaxSpeeds.FirstOrDefaultAsync
            (x => x.DeviceUniqueId == device.UniqueId && x.Type == detection.Type);
            
            if (IsLocationChanged(device.Latitude, device.Longitude, detections.Latitude, detections.Longitude, 0.009))
            {
                vehicleDeviceMaxSpeeds = null;
            }
            
            var maxSpeed = 0;
            if (vehicleDeviceMaxSpeeds != null)
            {
                maxSpeed = vehicleDeviceMaxSpeeds.MaxSpeed;
            }

            await _dbContext.Detections.AddAsync(new VehicleDetection
            {
                Speed = detection.Speed,
                MaxSpeed = maxSpeed,
                Time = detection.Time,
                Type = detection.Type,
                DeviceId = device.Id,
                Latitude = device.Latitude,
                Longitude = device.Longitude
            });
        }

        var res = await _dbContext.SaveChangesAsync();
        _logger.LogInformation($"Finished processing detections for {detections.MacAddress}");
        return res > 0 ? Ok() : BadRequest();
    }
}