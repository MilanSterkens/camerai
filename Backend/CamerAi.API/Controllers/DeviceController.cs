using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CamerAi.API.EntityFramework;
using CamerAi.API.Models;
using CamerAi.DAL.DTOs;

namespace CamerAi.API.Controllers
{
    [Route("[controller]")]
    [ApiController]
    public class DeviceController : ControllerBase
    {
        private readonly CamerAiDbContext _context;

        public DeviceController(CamerAiDbContext context)
        {
            _context = context;
        }

        // GET: api/Device
        [HttpGet]
        public async Task<ActionResult<IEnumerable<Device>>> GetDevices()
        {
            if (_context.Devices == null)
            {
                return NotFound();
            }
        
            return await _context.Devices.ToListAsync();
        }

        // GET: api/Device/5
        [HttpGet("{uniqueId}")]
        public async Task<ActionResult<IEnumerable<VehicleDeviceMaxSpeed>>> GetDevice(string uniqueId)
        {
            if (_context.VehicleDeviceMaxSpeeds == null)
            {
                return NotFound();
            }

            var devices = await _context.VehicleDeviceMaxSpeeds
                .Where(x => x.DeviceUniqueId == uniqueId)
                .ToListAsync();

            if (devices == null)
            {
                return NotFound();
            }

            return devices;
        }

        [HttpGet]
        [Route("getmaxspeedbydevice")]
        public async Task<ActionResult<MaxSpeedArray[]>> GetMaxSpeedByDevice(string uniqueId, double longitude, double latitude)
        {
            if (_context.VehicleDeviceMaxSpeeds == null)
            {
                return NotFound();
            }

            var maxSpeeds = await _context.VehicleDeviceMaxSpeeds
                .Where(x => x.DeviceUniqueId == uniqueId)
                .Where(x => x.Latitude == latitude)
                .Where(x => x.Longitude == longitude)
                .Select(x => new MaxSpeedArray {Type = x.Type, MaxSpeed = x.MaxSpeed})
                .ToArrayAsync();

            if (maxSpeeds.Length == 0)
            {
                maxSpeeds = new MaxSpeedArray[0];
            }

            return maxSpeeds;
        }

        [HttpPost]
        [Route("setmaxspeed")]
        public async Task<IActionResult> SetMaxSpeed(VehicleType vehicleType, int maxSpeed, string deviceUniqueId, double longitude, double latitude)
        {
            var type = await _context.VehicleDeviceMaxSpeeds.FirstOrDefaultAsync
                (x => x.Type == vehicleType 
                      && x.DeviceUniqueId == deviceUniqueId 
                      && x.Latitude == latitude
                      && x.Longitude == longitude);

            bool IsLocationChanged(double lat1, double lng1, double lat2, double lng2, double margin)
            {
                double latDiff = Math.Abs(lat1 - lat2);
                double lngDiff = Math.Abs(lng1 - lng2);

                return latDiff > margin || lngDiff > margin;
            }

            if (type != null)
            {
                if (IsLocationChanged(type.Latitude, type.Longitude, latitude, longitude, 0.009))
                {
                    type = null;
                }
            }

            if (type == null)
            {
                _context.VehicleDeviceMaxSpeeds
                    .Add(new VehicleDeviceMaxSpeed()
                    {
                        Type = vehicleType, DeviceUniqueId = deviceUniqueId, MaxSpeed = maxSpeed, Latitude = latitude,
                        Longitude = longitude
                    });
            }
            else
            {
                type.MaxSpeed = maxSpeed;
            }

            // change the maxspeed of all the detections that are already stored in the db
            var detections = _context.Detections
                .Where(x => x.Type == vehicleType 
                            && x.Device.UniqueId == deviceUniqueId 
                            && x.Latitude == latitude
                            && x.Longitude == longitude)
                .ToList();

            foreach (var detection in detections)
            {
                // if (detection.Device != null)
                // {
                //     double latDiff = Math.Abs(detection.Latitude - latitude);
                //     double lngDiff = Math.Abs(detection.Longitude - longitude);
                //
                //     if (latDiff > 0.009 || lngDiff > 0.009)
                //     {
                        detection.MaxSpeed = maxSpeed;
                //     }
                // }
               
            }

            await _context.SaveChangesAsync();
            return Ok();
        }

        // PUT: api/Device/5
        // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
        [HttpPut("{id}")]
        public async Task<IActionResult> PutDevice(int id, Device device)
        {
            if (id != device.Id)
            {
                return BadRequest();
            }

            _context.Entry(device).State = EntityState.Modified;

            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!DeviceExists(id))
                {
                    return NotFound();
                }
                else
                {
                    throw;
                }
            }

            return NoContent();
        }

        // POST: api/Device
        // To protect from overposting attacks, see https://go.microsoft.com/fwlink/?linkid=2123754
        [HttpPost]
        public async Task<ActionResult<Device>> PostDevice(Device device)
        {
            if (_context.Devices == null)
            {
                return Problem("Entity set 'CamerAiDbContext.Devices'  is null.");
            }

            _context.Devices.Add(device);
            await _context.SaveChangesAsync();

            return CreatedAtAction("GetDevice", new {id = device.Id}, device);
        }

        // DELETE: api/Device/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteDevice(int id)
        {
            if (_context.Devices == null)
            {
                return NotFound();
            }

            var device = await _context.Devices.FindAsync(id);
            if (device == null)
            {
                return NotFound();
            }

            _context.Devices.Remove(device);
            await _context.SaveChangesAsync();

            return NoContent();
        }

        private bool DeviceExists(int id)
        {
            return (_context.Devices?.Any(e => e.Id == id)).GetValueOrDefault();
        }
    }
}